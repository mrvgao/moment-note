# -*- coding:utf-8 -*-

from rest_framework.response import Response
from errors import codes


class SimpleResponse(Response):

    def __init__(self, data=None, success=True, message='', code=0, errors={}, **kwargs):
        status = kwargs.get('status', 200)
        response = {
            'request': 'success' if (success and not errors and status / 100 == 2 and code == 0) else 'fail',
        }
        if data is not None:
            if isinstance(data, Result):
                if not data.success:
                    errors = data.errors
                    response['request'] = 'fail'
                else:
                    data = data.data
            else:
                response['data'] = data
        if errors:
            response['errors'] = errors
        elif code != 0:
            response['errors'] = {
                'message': codes.messages.get(code, codes.DEFAULT_ERROR_MSG),
                'code': code
            }
        if not success and message:
            response.setdefault('errors', {})
            response['errors']['message'] = message
        super(SimpleResponse, self).__init__(response, **kwargs)


class Result:

    def __init__(self, data=None, success=True, code=0):
        if code != 0:
            self.success = False
            self.message = codes.messages.get(code, codes.DEFAULT_ERROR_MSG)
        else:
            self.success = success
            self.message = ''
        self.code = code
        self.data = data

    @property
    def errors(self):
        return {
            "message": self.message,
            "code": self.code,
        }
