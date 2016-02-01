# -*- coding:utf-8 -*-

import functools

from rest_framework import status

from errors import codes, exceptions
from .services import UserService


def check_request(target='user'):

    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            if target == 'user':
                id = kwargs.get('id')
                user = UserService.get_user(id=id)
                if not user:
                    raise exceptions.APIError(code=codes.USER_NOT_EXIST, status=status.HTTP_404_NOT_FOUND)
                else:
                    request.user = user
                    return func(self, request, *args, **kwargs)
            return func(self, request, *args, **kwargs)
        return wrapper
    return actual_decorator
