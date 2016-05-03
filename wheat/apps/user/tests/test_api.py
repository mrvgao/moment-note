'''
Test api functions.
@Author Minchiuan Gao <2016-4-20>
'''

from rest_framework.test import APITestCase
from settings import API_VERSION
from rest_framework.test import APIClient
from apps.user.services import user_service
from errors import codes
from django.contrib.auth import authenticate
from apps.user.models import User, AuthToken


URL_PREFIX = '/api/%s/' % API_VERSION


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
        self._send_register_info(phone=error_phone, if_registered=False)

        right_phone = self.phone
        self._send_register_info(phone=right_phone, if_registered=True)

        null_phone = ''  # test blank
        self._send_register_info(phone=null_phone, if_registered=False)

    def _send_register_info(self, phone, if_registered):
        base_url = URL_PREFIX + 'users/register/'
        url = base_url + '?phone=' + phone

        client = APIClient()
        client.credentials(enforce_csrf_checks=False)
        response = client.get(url)

        self.assertEqual(response.status_code, 200)
        
        rsp_data = response.data['data']
        self.assertEqual(rsp_data['registered'], if_registered)
        self.assertEqual(rsp_data['phone'], phone)

    def test_set_password(self):

        new_password = 'miffy'

        post_data = {
            'phone': self.phone,
            'password': new_password
        }

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
        response = self.client.post(url, post_data)

        self.assertEqual(response.data['errors']['code'], codes.PHONE_NUMBER_NOT_EXIST)

    def test_invalid_registed(self):
        post_data = {
            'phone': '110',
            'password': '123'
        }

        url = URL_PREFIX + 'users/'
        response = self.client.post(url, post_data)

        self.assertTrue('errors' in response.data)
        self.assertEqual(response.data['errors']['code'], codes.INVALID_REG_INFO)

    def test_registed_again(self):
        post_data = {
            'phone': self.phone,
            'password': 'some-password'
        }

        url = URL_PREFIX + 'users/'
        response = self.client.post(url, post_data)

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

        self.assertTrue('data' in response.data)
        self.assertEqual(response.data['data']['phone'], new_numbner)

        user = User.objects.get(phone=new_numbner)
        self.assertIsNotNone(user)

        token = AuthToken.objects.get(user_id=user.id)
        user_token = response.data['data']['token']['token']
        self.assertEqual(token.key, user_token)
        self.assertFalse(token.expired())

    def test_destroy_success(self):
        self.user.is_admin = True
        self.user.save()
        self.update_client_token(self.phone, self.password)

        user_id = self.user.id
        url = URL_PREFIX + 'users/{0}/'.format(user_id)
        response = self.client.delete(url)

        self.assertEqual(response.data['data']['id'], str(user_id))

        user = user_service.get(id=user_id)
        self.assertTrue(user.deleted)

    def test_login_success(self):
        response = self.login(self.phone, self.password)

        self.assertEqual(response.data['data']['phone'], self.phone)
        user_id = response.data['data']['id']

        token = AuthToken.objects.get(user_id=user_id)
        user_token = response.data['data']['token']['token']
        self.assertEqual(token.key, user_token)
        self.assertFalse(token.expired())

    def test_login_failed(self):
        response = self.login(self.phone, 'wrong-pwd')
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
        
    def update_client_token(self, phone, password):
        response = self.login(phone, password)
        user_token = response.data['data']['token']['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        
    def test_set_avatar(self):
        self.update_client_token(self.phone, self.password)

        post_data = {
            'avatar': 'new-avatar',
            'user_id': str(self.user.id)
        }

        old_avatar = self.user.avatar

        set_avatar_url = URL_PREFIX + 'users/avatar/'
        response = self.client.put(set_avatar_url, post_data)
        self.assertNotEqual(response.data['data']['avatar'], old_avatar)


def TestUserViewSet(TestCase):
    def test_register_user(self):
        pass
