# -*- coding:utf-8 -*-

import functools
from rest_framework import status

from errors import codes, exceptions
from apps.user.services import UserService
from .services import GroupService


def check_group_auth(auth='invitation'):

    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            if auth == 'invitation':
                group_id = kwargs.get('id')
                group = GroupService.get_group(id=group_id)
                if not group:
                    raise exceptions.APIError(code=codes.UNKNOWN_GROUP, status=status.HTTP_404_NOT_FOUND)
                else:
                    if not isinstance(request.user, UserService._get_model()):
                        raise exceptions.APIError(code=codes.LOGIN_REQUIRED, status=status.HTTP_401_UNAUTHORIZED)
                    if str(request.user.id) not in group.members:
                        raise exceptions.APIError(code=codes.HAS_NO_PERMISSION, status=status.HTTP_403_FORBIDDEN)
                    request.group = group
                    return func(self, request, *args, **kwargs)
            return func(self, request, *args, **kwargs)
        return wrapper
    return actual_decorator
