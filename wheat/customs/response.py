# -*- coding:utf-8 -*-

from rest_framework.response import Response
from errors import codes


class R(object):
    def __init__(self):
        self.__success = True
        self.__error = None
        self.data = None

    @property
    def success(self):
        return 'success' if self.__success else 'fail'

    @property
    def response(self):
        return {
            'request': self.success,
            'errors': self.error,
            'data': self.data
        }
        
    @property
    def error(self):
        return self.__error

    @error.setter
    def error(self, error_code):
        self.__success = False
        self.__error = codes.errors(error_code)


class APIResponse(Response):
    '''
    API response for django restful
    '''
    def __init__(self, result, status=200, **kwargs):

        r = R()

        if isinstance(result,  int):
            r.error = result
        elif isinstance(result, dict):
            r.data = result
        else:
            raise TypeError('{0} unsupport type, return type must be json'.format(result))

        response = r.response

        super(APIResponse, self).__init__(response, status=status,  **kwargs)


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

    def __init__(self, data=None, code=codes.OK):
        if code != codes.OK:
            self.success = False
            self.message = codes.messages.get(code, codes.DEFAULT_ERROR_MSG)
        else:
            self.success = True
            self.message = codes.OK_MSG
        self.code = code
        self.data = data

    @property
    def errors(self):
        return {
            "message": self.message,
            "code": self.code,
        }


