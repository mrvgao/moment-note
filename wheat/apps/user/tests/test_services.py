'''
Test for services.
@Author Minchiuan Gao <2016-4-20>
'''

from django.test import TestCase
from apps.user.models import AuthToken
from apps.user.models import User
from apps.user.models import Relationship
from apps.user.models import FriendShip
from apps.user.services import UserService


class UserServiceTestCase(TestCase):
    def test_get_model(self):
        USER = 'User'
        user_cls = UserService._get_model(USER)
        self.assertEqual(user_cls.__name__, USER)

        # check defalut paramter.
        user_cls = UserService._get_model()
        self.assertEqual(user_cls.__name__, USER)

        # check get auth token
        user_cls = UserService._get_model('AuthToken')
        self.assertEqual(user_cls.__name__, 'AuthToken')

        
    
