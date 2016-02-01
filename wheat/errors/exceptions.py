# -*- coding:utf-8 -*-

from json import JSONEncoder
import logging

from rest_framework import status
from rest_framework import exceptions
from django.utils.translation import ugettext_lazy as _

from errors import codes

logger = logging.getLogger('exception')


class APIError(exceptions.APIException):

    """
    Modified rest_framework's APIException to add more detail of the errors.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _(codes.DEFAULT_ERROR_MSG)

    def __init__(self, code=0, status=status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.detail = {
            'request': 'fail',
        }
        if code != 0:
            self.detail['errors'] = {
                'message': codes.messages.get(code, codes.DEFAULT_ERROR_MSG),
                'code': code
            }
        APIError.status_code = status
        logger.error(JSONEncoder().encode(self.detail))

    def __str__(self):
        return JSONEncoder().encode(self.detail)
