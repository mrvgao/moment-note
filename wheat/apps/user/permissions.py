# -*- coding:utf-8 -*-

import functools

from django.contrib.auth.models import AnonymousUser
from rest_framework import status

from errors import codes, exceptions
from .services import UserService
from datetime import datetime
import hashlib

KEY = 'Ma1@Li'
HOUR = datetime.now().hour
DELTA = 97
CODE = HOUR * DELTA


def encode(msg):
    m = hashlib.md5()
    m.update(msg)
    x = m.hexdigest()
    return x


def encode_maili():
    origin_code = KEY + str(CODE)
    return encode(origin_code)


def valid(key):
    origin_code = KEY + str(CODE)
    if key == encode(origin_code):
        return True
    return False


def check_token(func):
    @functools.wraps(func)
    def token_valid(self, request, *args, **kwargs):
        key = request.META.get('HTTP_KEY') or request.META.get('KEY')
        if not key or not valid(key):
            raise exceptions.APIError(code=codes.HAS_NO_PERMISSION, status=status.HTTP_403_FORBIDDEN)
        else:
            return func(self, request, *args, **kwargs)
    return token_valid


def login_required(func):
    @functools.wraps(func)
    def func_wrapper(self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            raise exceptions.APIError(code=codes.LOGIN_REQUIRED, status=status.HTTP_401_UNAUTHORIZED)
        elif request.user.token_expired:
            raise exceptions.APIError(code=codes.INVALID_TOKEN, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return func(self, request, *args, **kwargs)
    return func_wrapper


def user_is_same_as_logined_user(func):
    @functools.wraps(func)
    def check(self, request, *args, **kwargs):
        USER_ID = 'user_id'
        if USER_ID not in request.data:
            raise exceptions.APIError(
                code=codes.LACK_USER_ID_MSG,
                status=status.HTTP_403_FORBIDDEN
            )
        if str(request.data[USER_ID]) != str(request.user.id):
            raise exceptions.APIError(
                code=codes.UNVALID_USER_ID_MSG,
                status=status.HTTP_401_UNAUTHORIZED)
        else:
            return func(self, request, *args, **kwargs)
    return check


def admin_required(func):
    @functools.wraps(func)
    def func_wrapper(self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            raise exceptions.APIError(code=codes.ADMIN_REQUIRED, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        elif request.user and request.user.is_admin:
            return func(self, request, *args, **kwargs)
        else:
            raise exceptions.APIError(code=codes.ADMIN_REQUIRED, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return func_wrapper


def is_userself(func):
    @functools.wraps(func)
    def account_wrapper(self, request, id, *args, **kwargs):
        account = UserService.get_user(id=id)
        if isinstance(request.user, AnonymousUser):
            raise exceptions.APIError(code=codes.HAS_NO_PERMISSION, status=status.HTTP_403_FORBIDDEN)
        elif account == request.user or (request.user and request.user.is_admin):
            return func(self, request, id, *args, **kwargs)
        else:
            raise exceptions.APIError(code=codes.HAS_NO_PERMISSION, status=status.HTTP_403_FORBIDDEN)
    return account_wrapper
