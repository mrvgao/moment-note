'''
Test api functions.
@Author Minchiuan Gao <2016-4-20>
'''

from rest_framework.test import APITestCase
from settings import API_VERSION
from rest_framework.test import APIClient
from apps.user.services import user_service


URL_PREFIX = '/api/%s/' % API_VERSION


class UserViewSetTest(APITestCase):
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

        url = URL_PREFIX + 'users/password/'

        response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 200)

        self.assertTrue(isinstance(response.data, dict))
        self.assertTrue('data' in response.data)

        rsp_data = response.data['data']

        self.assertEqual(rsp_data['phone'], self.phone)

    def test_check_if_registed(self):
        pass

    def test_register_user_method(self):
        pass

    def test_destroy(self):
        pass

    def test_login(self):
        pass

    def test_check_user_valid(self):
        pass

    def test_set_avatar(self):
        pass

    def test_if_online(self):
        pass
