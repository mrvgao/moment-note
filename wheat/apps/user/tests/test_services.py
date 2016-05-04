'''
Test for services.
@Author Minchiuan Gao <2016-4-20>
'''

from django.test import TestCase
from apps.user.models import User
from apps.user.models import Captcha
from apps.user.services import UserService
from apps.user.services import captcha_service
from apps.user.services import auth_service
from django.conf import settings
from django.utils.importlib import import_module
from django.http import HttpRequest
import datetime

user_service = UserService()


class UserServiceTestCase(TestCase):
    def test_registe_info_check(self):
        phone = '18857453090'
        password = '123456'

        valid, registed_again = user_service.check_register_info(phone, password)
        self.assertTrue(valid)
        self.assertFalse(registed_again)

        User.objects.create(phone=phone)

        valid, registed_again = user_service.check_register_info(phone, password)
        self.assertTrue(valid)
        self.assertTrue(registed_again)

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


class UserInfoModificationTestCase(TestCase):
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

    def test_change_password_by_phone_and_password(self):
        phone = self.test_phone
        old_password = self.test_user.password

        user = user_service.get(phone=phone)
        self.assertEqual(user.password, old_password)  # ensure test

        new_user = user_service.set_password_by_phone_and_password(phone, 'new-password')
        user = user_service.get(phone=phone)
        self.assertIsNotNone(user)
        self.assertNotEqual(user.password, old_password)

        phone = '12345678910'
        new_user = user_service.set_password_by_phone_and_password(phone, 'new-password')
        self.assertIsNone(new_user)   # if no this user, return none.

    def test_update_by_id(self):
        # test for valid update
        id = self.test_user.id
        user = user_service.get(id=id)
        self.assertEqual(user.phone, self.test_phone)

        new_phone = '18857453099'
        new_user = user_service.update_by_id(id, phone=new_phone)

        self.assertEqual(new_user.phone, new_phone)
        user = user_service.get(id=id)
        self.assertEqual(user.phone, new_phone)

    def test_check_register_info_valid(self):
        valid = user_service.check_info_formatted('some-phone', 'some-pwd')
        self.assertFalse(valid)

        valid = user_service.check_info_formatted('18857453090', 'some-pwd')
        self.assertTrue(valid)

    def test_if_credential(self):
        valid = user_service.check_if_credential(self.test_phone, self.test_password)
        self.assertTrue(valid)
        
        invalid = user_service.check_if_credential(self.test_phone, 'wrong-pwd')
        self.assertFalse(invalid)

        invalid = user_service.check_if_credential('wrong-number', self.test_password)
        self.assertFalse(invalid)

        invalid = user_service.check_if_credential('wrong-number', 'wrong-pwd')
        self.assertFalse(invalid)

    def test_if_activated(self):
        activaed = user_service.check_if_activated(self.test_phone)
        self.assertTrue(activaed)

        inactivated = user_service.check_if_activated('some-phone')
        self.assertFalse(inactivated)

    def test_login(self):
        user = user_service.login_user(self.test_phone, self.test_password)
        self.assertIsNotNone(user)

        user = user_service.login_user(self.test_phone, 'some-pwd')
        self.assertIsNone(user)


class ServiceCommunicationWithAPITestCase(TestCase):
    def setUp(self):
        self.request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.exist_phone = '18857453090'
        self.password = '123456'
        self.exist_user = user_service.create(self.exist_phone, self.password)

    def test_register(self):
        new_phone = '18857453099'
        password = 'somepass'
        user = user_service.register(new_phone, password)
        self.assertIsNotNone(user)
        self.assertEqual(user.phone, new_phone)
        self.assertTrue(hasattr(user, 'token'))
        self.assertTrue('token' in user.token)

    def test_cannot_register_duplcaite(self):
        user = user_service.register(self.exist_phone, 'somepassword')
        self.assertIsNone(user)

    def test_login_inactivaed(self):
        user = User.objects.get(phone=self.exist_phone)
        user.activated = False
        user.save()


class TestCaptchaService(TestCase):
    def setUp(self):
        self.phone = '18857453090'
        self.old_phone = '18857453099'
        self.captcha = Captcha.objects.create(phone=self.phone, code='123456')
        self.old_captcha = Captcha.objects.create(
            phone=self.old_phone, code='111111',
        )
        self.old_captcha.created_at = datetime.datetime(2014, 1, 1)
        self.old_captcha.save()

    def test_get_new_captcha(self):
        captcha_code = captcha_service.get_new_captch(self.phone)
        self.assertEqual(len(captcha_code), 6)

        new_code = captcha_service.get_new_captch(self.old_phone)
        self.assertNotEqual(captcha_code, new_code)

    def test_expired(self):
        unexipred = captcha_service._expired(self.captcha)
        self.assertFalse(unexipred)
        
        exipred = captcha_service._expired(self.old_captcha)
        self.assertTrue(exipred)

    def test_get_captcha_from_obj(self):
        code = captcha_service.get_captcha_code_from_obj(self.captcha)
        self.assertEqual(code, self.captcha.code)
        
        old_code = self.old_captcha.code
        new_code = captcha_service.get_captcha_code_from_obj(self.old_captcha)
        self.assertNotEqual(new_code, old_code)

    def test_get_captch(self):
        code = self.captcha.code
        new_code = captcha_service.get_captch(self.phone)
        self.assertEqual(code, new_code)

        code = self.old_captcha.code
        new_code = captcha_service.get_captch(self.old_phone)
        self.assertNotEqual(code, new_code)

    def test_get_captch_with_new_phone(self):
        phone_number = '13993300082'
        code = captcha_service.get_captch(phone_number)
        self.assertIsNotNone(code)
        
        self.assertIsNotNone(Captcha.objects.get(phone=phone_number))

        code_again = captcha_service.get_captch(phone_number)
        self.assertEqual(code_again, code)

    def _test_send_message(self):
        send = captcha_service.send_captcha(self.phone, self.captcha.code)
        self.assertTrue(send)

    def test_check_captcha(self):
        code = self.captcha.code
        valid = captcha_service.check_captcha(self.phone, code)
        self.assertTrue(valid)

        invalid = captcha_service.check_captcha('some-phone', code)
        self.assertFalse(invalid)

        old_code = self.old_captcha.code
        invalid = captcha_service.check_captcha(self.old_phone, old_code)
        self.assertFalse(invalid)
        

class TestAuthService(TestCase):
    pass


class TetstFriendship(TestCase):
    pass
