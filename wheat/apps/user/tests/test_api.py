'''
Test api functions.
@Author Minchiuan Gao <2016-4-20>
'''

from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from apps.user.services import user_service
from errors import codes, exceptions
from django.contrib.auth import authenticate
from apps.user.models import User, AuthToken
from apps.user.permissions import encode_maili
from customs.test_tools import login_client
from customs.test_tools import refresh_token
from customs.test_tools import URL_PREFIX


class UserAPITest(APITestCase):
    def setUp(self):
        self.phone = '18857453090'
        self.password = '12345678'
        self.user = user_service.create(self.phone, self.password)
        self.client = APIClient()
        self.client.credentials(enforce_csrf_checks=False)
    
    def test_account_if_registed(self):
        '''
        Test a phone number if has been registered.
        '''
        error_phone = '18857453091'   # this phone no registed
        self._send_register_info(phone=error_phone, if_registered=False, status=200)

        right_phone = self.phone
        self._send_register_info(phone=right_phone, if_registered=True, status=409)

        null_phone = ''  # test blank
        self._send_register_info(phone=null_phone, if_registered=False, status=200)

    def _send_register_info(self, phone, if_registered, status):
        base_url = URL_PREFIX + 'users/register/'
        url = base_url + '?phone=' + phone

        client = APIClient()
        client.credentials(enforce_csrf_checks=False)
        response = client.get(url)

        self.assertEqual(response.status_code, status)
        
        rsp_data = response.data['data']
        self.assertEqual(rsp_data['registered'], if_registered)
        self.assertEqual(rsp_data['phone'], phone)

    def test_set_password(self):

        new_password = 'miffy'

        post_data = {
            'phone': self.phone,
            'password': new_password
        }

        refresh_token(self.client, self.phone, self.password)

        invalid_user = authenticate(username=self.phone, password=new_password)
        self.assertIsNone(invalid_user)

        valid_user = authenticate(username=self.phone, password=self.phone)
        self.assertIsNone(valid_user)

        url = URL_PREFIX + 'users/password/'
        response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 200)

        self.assertTrue(isinstance(response.data, dict))
        self.assertTrue('data' in response.data)

        rsp_data = response.data['data']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(rsp_data['phone'], self.phone)

        invalid_user = authenticate(username=self.phone, password=self.phone)
        self.assertIsNone(invalid_user)

        valid_user = authenticate(username=self.phone, password=new_password)
        self.assertIsNotNone(valid_user)

    def test_set_password_faild(self):
        post_data = {
            'phone': 'some-phone',
            'password': 'some-pwd'
        }

        url = URL_PREFIX + 'users/password/'
        login_client(self.client, self.phone, self.password)
        response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['errors']['code'], codes.LOGIN_REQUIRED)

    def test_invalid_registed(self):
        post_data = {
            'phone': '110',
            'password': '123'
        }

        url = URL_PREFIX + 'users/'
        response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 406)
        self.assertTrue('errors' in response.data)
        self.assertEqual(response.data['errors']['code'], codes.INVALID_REG_INFO)

    def test_registed_again(self):
        post_data = {
            'phone': self.phone,
            'password': 'some-password'
        }

        url = URL_PREFIX + 'users/'
        response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 409)
        self.assertTrue('errors' in response.data)
        self.assertEqual(response.data['errors']['code'], codes.PHONE_ALREAD_EXIST)

    def test_registed_success(self):
        new_numbner = '13993300082'

        post_data = {
            'phone': '13993300082',
            'password': 'some-password'
        }

        url = URL_PREFIX + 'users/'
        response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue('data' in response.data)
        self.assertEqual(response.data['data']['phone'], new_numbner)

        user = User.objects.get(phone=new_numbner)
        self.assertIsNotNone(user)

        token = AuthToken.objects.get(user_id=user.id)
        user_token = response.data['data']['token']['token']
        self.assertEqual(token.key, user_token)
        self.assertFalse(token.expired())

    def _test_destroy_success(self):
        self.user.is_admin = True
        self.user.save()
        refresh_token(self.client, self.phone, self.password)

        user_id = self.user.id
        url = URL_PREFIX + 'users/{0}/'.format(user_id)
        response = self.client.delete(url)

        self.assertEqual(response.data['data']['id'], str(user_id))

        user = user_service.get(id=user_id)
        self.assertTrue(user.deleted)

    def test_login_success(self):
        response = self.login(self.phone, self.password)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['phone'], self.phone)
        user_id = response.data['data']['id']

        token = AuthToken.objects.get(user_id=user_id)
        user_token = response.data['data']['token']['token']
        self.assertEqual(token.key, user_token)
        self.assertFalse(token.expired())

    def test_login_failed(self):
        response = self.login(self.phone, 'wrong-pwd')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['request'], 'fail')
        self.assertEqual(response.data['errors']['code'], codes.INCORRECT_CREDENTIAL)
        
    def login(self, phone, password):
        url = URL_PREFIX + 'users/login/'
        post_data = {
            'phone': phone,
            'password': password
        }
        response = self.client.post(url, post_data)
        return response
        
    def test_set_avatar(self):
        refresh_token(self.client, self.phone, self.password)
        post_data = {
            'avatar': 'new-avatar',
            'user_id': str(self.user.id)
        }

        old_avatar = self.user.avatar

        set_avatar_url = URL_PREFIX + 'users/avatar/'
        response = self.client.put(set_avatar_url, post_data)
        self.assertNotEqual(response.data['data']['avatar'], old_avatar)

    def test_get_defalut_home(self):
        refresh_token(self.client, self.phone, self.password)

        url = URL_PREFIX + 'users/home/'
        response = self.client.get(url)

        print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_get_joined_home(self):
        refresh_token(self.client, self.phone, self.password)
        url = URL_PREFIX + 'users/homes/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        print(response.data)
        self.assertTrue('homes' in response.data['data'])
        

class TestTokenViewSet(APITestCase):
    def setUp(self):
        self.phone = '18857453090'
        self.password = '12345678'
        self.user = user_service.create(self.phone, self.password)
        self.client = APIClient()
        self.client.credentials(enforce_csrf_checks=False)
        self.login(self.phone, self.password)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user.token['token'])

    def login(self, phone, password):
        url = URL_PREFIX + 'users/login/'
        post_data = {
            'phone': phone,
            'password': password
        }
        response = self.client.post(url, post_data, format='json')
        return response
     
    def test_refesh_token(self):
        put_data = {
            'user_id': str(self.user.id),
            'token': self.user.token['token']
        }

        key = AuthToken.objects.get(user_id=str(self.user.id)).key
        
        url = URL_PREFIX + 'token/refresh/'
        response = self.client.put(url, put_data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['user_id'], str(self.user.id))

        self.assertNotEqual(response.data['data']['new_token'], key)
        user_token = User.objects.get(id=self.user.id).token['token']
        self.assertEqual(response.data['data']['new_token'], user_token)

    def test_check_token_valid(self):
        token = self.user.token['token']

        url = URL_PREFIX + 'token/{0}/valid/'.format(token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['data']['valid'])

        token = 'some-wrong-token'
        url = URL_PREFIX + 'token/{0}/valid/'.format(token)
        response = self.client.get(url)
        self.assertFalse(response.data['data']['valid'])


class TestCaptchaViewSet(APITestCase):
    def test_get_captcha(self):
        phone = '18857453090'
        url = URL_PREFIX + 'captcha/{0}/'.format(phone)
        code = encode_maili()
        response = self.client.get(url, **{'KEY': code})
        self.assertEqual(response.status_code, 200)

        first_captcha = response.data['data']['captcha']
        self.assertEqual(response.data['data']['phone'], phone)
        self.assertIsNotNone(response.data['data']['captcha'])
        self.assertEqual(len(response.data['data']['captcha']), 6)

        response = self.client.get(url, **{'KEY': 'arbitary-code'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url, **{'KEY': code})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data['data']['captcha'], first_captcha)

        url = URL_PREFIX + 'captcha/{0}/'.format('13993300082')
        response = self.client.get(url, **{'KEY': code})
        self.assertEqual(response.status_code, 200)

        self.assertNotEqual(response.data['data']['captcha'], first_captcha)

    def _test_send_captcha(self):
        phone = '18857453090'
        url = URL_PREFIX + 'captcha/{0}/send/'.format(phone)
        code = encode_maili()
        response = self.client.get(url, **{'KEY': code})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']['captcha']), 6)

        url = URL_PREFIX + 'captcha/{0}/send/'.format('noaphone')
        response = self.client.get(url, **{'KEY': code})
        self.assertEqual(response.status_code, 408)
        self.assertEqual(response.data['request'], 'fail')
        

    
