# -*- coding:utf-8 -*-

import functools

from django.contrib.auth.models import AnonymousUser
from rest_framework import status

from errors import codes, exceptions
from .services import UserService


def login_required(func):
    @functools.wraps(func)
    def func_wrapper(self, request, *args, **kwargs):
        if not isinstance(request.user, UserService._get_model()):
            raise exceptions.APIError(code=codes.LOGIN_REQUIRED, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return func(self, request, *args, **kwargs)
    return func_wrapper


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
