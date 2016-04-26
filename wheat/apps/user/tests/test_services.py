'''
Test for services.
@Author Minchiuan Gao <2016-4-20>
'''

from django.test import TestCase
from apps.user.models import AuthToken
from apps.user.models import User
from apps.user.models import Relationship
from apps.user.models import FriendShip
from apps.user.services import user_service


class UserServiceTestCase(TestCase):
    def test_create_new_user(self):
        original_pwd = '1234567'
        original_phone = '18857453090'
        user = user_service.create(phone=original_phone, password=original_pwd)

        password = user.password

        self.assertTrue(User.objects.filter(phone=original_phone).exists())
        self.assertTrue(User.objects.filter(id=user.id).exists())
        self.assertNotEqual(original_pwd, password)
        self.assertEqual(user.phone, original_phone)
        self.assertEqual(user.gender, 'N')
        self.assertEqual(user.activated, True)

    def test_create_new_with_unwritable_feilds(self):
        user = user_service.create(phone='13993300001', password='1234566', activated=False)
        self.assertEqual(user.activated, True)

    def test_update_user(self):
        user = user_service.create(phone='13993300001', password='1234566', activated=False)
        formal_psw = user.password
        user = user_service.update(user, gender='M')
        self.assertEqual(user.gender, 'M')

        new_password = 'miffy'
        user = user_service.update(user, password=new_password)
        new_pwd = user.password
        self.assertIsNotNone(user.password)
        self.assertEqual(formal_psw, new_pwd)
        # password could not update by update() method direcly.

    def test_delete_user(self):
        user = user_service.create(phone='13993300001', password='1234566', activated=False)
        user = user_service.lazy_delete_user(user)
        self.assertTrue(user.deleted)

    def test_get_captcha(self):
        pass

    def test_creat_friendship(self):
        pass

    def test_if_registed(self):
        '''
        Test if user has registed. if registerd, return True, return False if not.
        '''

        phone = '18857453090'
        registered = user_service.check_if_registed(phone)
        self.assertFalse(registered)


class TestUserInfoModification(TestCase):
    def setUp(self):
        self.test_phone = '18857453090'
        self.test_password = '123456'
        self.test_user = user_service.create(phone=self.test_phone, password=self.test_password)

    def test_change_passwod(self):
        new_password = '654321'
        old_password = self.test_user.password
        user_service.set_password(self.test_user, new_password)
        self.assertNotEqual(self.test_user.password, old_password)

    def test_delete_user(self):
        user_id = self.test_user.id
        self.test_user = user_service.delete(user_id)
        self.assertTrue(self.test_user.deleted)


class TestUserCommunicationWithAPI(TestCase):
    phone = '18857453090'
    pwd = '12345678'
    gender = 'M'

    def test_register(self):
        user = user_service.register(self.phone, self.pwd, gender=self.gender)
        self.assertTrue(isinstance(user, dict))
        self.assertTrue('phone' in user)
        self.assertTrue('password' not in user)
        # password field is invisible in serialize data
        self.assertTrue('gender' in user)

    def test_cannot_register_again(self):
        user = user_service.register(self.phone, self.pwd, gender=self.gender)
        self.assertIsNotNone(user)
        over_user = user_service.register(self.phone, self.pwd, gender=self.gender)
        self.assertIsNone(over_user)

    
        
