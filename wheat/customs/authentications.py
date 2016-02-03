# -*- coding:utf-8 -*-

import logging

from rest_framework.authentication import (SessionAuthentication, BaseAuthentication,
                                           get_authorization_header)
from rest_framework import status
from django.contrib.auth.models import AnonymousUser

from apps.user.models import AuthToken
from errors import exceptions, codes

logger = logging.getLogger('auth')


class LocalSessionAuthentication(SessionAuthentication):

    def authenticate(self, request):
        http_request = request._request
        user = getattr(http_request, 'user', None)

        if not user or not user.activated:
            return None

        return (user, None)


class AllowAllAuthentication(BaseAuthentication):

    def authenticate(self, request):
        return None


class XTokenAuthentication(BaseAuthentication):

    auth_model = AuthToken

    def __init__(self, *args, **kwargs):
        super(XTokenAuthentication, self).__init__(*args, **kwargs)
        self.user = AnonymousUser()
        self.token = None
        self.key = None

    def authenticate(self, request):
        header = get_authorization_header(request)
        auth = header.split()
        if not auth or auth[0].lower() not in [b'token', b'post']:
            return None
        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            logger.error('%s: %s' % (msg, header))
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            logger.error('%s: %s' % (msg, header))
            raise exceptions.AuthenticationFailed(msg)
        is_auth_token = True if auth[0].lower() == b'token' else False
        return self.authenticate_credentials(is_auth_token, auth[1])

    def authenticate_credentials(self, is_auth_token, key):
        if key is not None and key == self.key:
            return (self.user, self.token)
        if is_auth_token:
            token = self.auth_model.objects.get_or_none(key=key)
            if token is None:
                logger.error('auth token not exists error: code(%d), status(401), key(%s)' % (
                    codes.INVALID_TOKEN, key))
                raise exceptions.APIError(code=codes.INVALID_TOKEN, status=status.HTTP_401_UNAUTHORIZED)
            elif not token.user.activated:
                logger.error('auth token user not activated error: code(%d), status(401), key(%s)' % (
                    codes.INACTIVE_ACCOUNT, key))
                raise exceptions.APIError(code=codes.INACTIVE_ACCOUNT, status=status.HTTP_401_UNAUTHORIZED)
            elif token.expired():
                logger.error('auth token expired error: code(%d), status(401), key(%s)' % (
                    codes.EXPIRED_TOKEN, key))
                raise exceptions.APIError(code=codes.EXPIRED_TOKEN, status=status.HTTP_401_UNAUTHORIZED)
            self.user = token.user
            self.token = token
            self.key = key
            return (self.user, self.token)
        else:
            logger.error('auth token not exists error: code(%d), status(401), key(%s)' % (
                codes.INVALID_TOKEN, key))
            raise exceptions.APIError(code=codes.INVALID_TOKEN, status=status.HTTP_401_UNAUTHORIZED)

    def authenticate_header(self, request):
        return 'Token'
