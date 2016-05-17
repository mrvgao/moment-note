'''
Some utils from request.
'''

import functools
from errors import codes, exceptions
from rest_framework import status
import unicodedata
import functools


def change_unicode_to_str(unicode_dict):
    request_data = {}
    for k, v in unicode_dict.iteritems():
        value = v
        str_value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        str_key = unicodedata.normalize('NFKD', k).encode('ascii', 'ignore')
        request_data[str_key] = str_value
    return request_data


def post_data_check(required_args):
    def check(func):
        wrap = _check(func, required_args)
        return wrap
    return check


def _check(func, required_args):
    @functools.wraps(func)
    def wrap(viewset, request, *arg, **kwargs):
        for param in required_args:
            if param not in request.data:
                raise exceptions.APIError(code=codes.LACK_REQUIRED_PARAM, status=status.HTTP_400_BAD_REQUEST)
        else:
            return func(viewset, request, **kwargs)
    return wrap
