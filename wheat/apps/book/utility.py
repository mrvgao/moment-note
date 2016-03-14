'''
Book Utilities.

Author: Minchiuan Gao 2016-3-14

'''

import collections
import requests
from errors.exceptions import APIError
from errors import codes
from rest_framework import status


WXBOOK_URL = 'http://open.weixinshu.com/maili/login/{}'
#WXBOOK_URL = 'http://192.168.0.126:8009/maili/login/{}'


def login_wxbook(func):
    def send_id_to_wx_book(self, request, *args, **kwargs):
        user_id = request.user.id
        url = WXBOOK_URL.format(str(user_id))
        r = requests.get(url)
        response = r.json()
        STATUS, SUCCESS = 'status', 'success'
        if response[STATUS] == SUCCESS:
            return func(self, request, *args, **kwargs)
        else:
            raise ValueError

    return send_id_to_wx_book


@login_wxbook
def test_decorator(request, test_id):
    pass


def test():
    Request = collections.namedtuple('Request', ['user'])
    User = collections.namedtuple('User', ['id'])
    user_id = 'c24178cb20704c11a9abfd709b12179d'
    user = User(user_id)
    request = Request(user)
    try:
        test_decorator(request, 'teste')
        print('login success')
    except ValueError:
        print('login wxbook is error, check user id or net connection')
    finally:
        print('connect to wx end')


if __name__ == '__main__':
    test()
