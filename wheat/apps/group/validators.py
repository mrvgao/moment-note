# -*- coding:utf-8 -*-

import functools

from rest_framework import status

from errors import codes, exceptions
from .services import InvitationService


def check_request(target='invitation'):

    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            if target == 'invitation':
                id = kwargs.get('id')
                invitation = InvitationService().get(id=id)
                if not invitation:
                    raise exceptions.APIError(code=codes.NOT_EXIST, status=status.HTTP_404_NOT_FOUND)
                else:
                    request.invitation = invitation
                    return func(self, request, *args, **kwargs)
            return func(self, request, *args, **kwargs)
        return wrapper
    return actual_decorator
