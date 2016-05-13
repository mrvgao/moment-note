'''
Some utils from request.
'''

import functools
from errors import codes, exceptions
from rest_framework import status


def post_data_check(required_args):
    def check(func):
        wrap = functools.partial(_check, func, required_args)
        return wrap
    return check
        

def _check(func, required_args, viewset, request, *args, **kwargs):
    for args in required_args:
        if args not in request.data:
            raise exceptions.APIError(code=codes.LACK_REQUIRED_PARAM, status=status.HTTP_400_BAD_REQUEST)
    else:
        return func(viewset, request, *args, **kwargs)