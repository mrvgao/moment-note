'''
Test api functions.
@Author Minchiuan Gao <2016-4-20>
'''

from rest_framework.test import APITestCase
from settings import API_VERSION
from rest_framework.test import force_authenticate
from rest_framework.test import APIClient


URL_PREFIX = '/api/%s/' % API_VERSION


class AccountTest(APITestCase):
    def set_up(self):
        pass
    
    def test_account_have_registed(self):
        '''
        Test a phone number if has been registered.
        '''
        url = URL_PREFIX + 'users/register/'
        phone = '18857453090'
        url = url + '?phone=' + phone
        t_url = '/api/0.1/user/register/?phone=18857453090'
        client = APIClient()
        client.credentials(enforce_csrf_checks=False)
        response = client.get(url)
        print(url)
        print(t_url)
        self.assertEqual(response.status_code, 200)
        rsp_data = response.data['data']
        self.assertEqual(rsp_data['registered'], False)
        self.assertTrue('phone' in rsp_data)
        self.assertEqual(rsp_data['phone'], phone)

