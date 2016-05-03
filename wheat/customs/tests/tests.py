from django.test import TestCase
from customs.urls import get_urlpattern
from customs.urls import get_url
from customs import class_tools
from apps.user.services import user_service
from customs import response


class TestUrlUtils(TestCase):
    def test_get_complete_url(self):
        api_name = 'user'
        resource = '/001/'

        complete_url = get_url(api_name, resource)
        self.assertEqual(complete_url, '/api/0.1/user/001/')

    def test_get_urlpattern(self):
        api_name = 'test'
        u_p = get_urlpattern({}, api_name)
        self.assertIsNotNone(u_p)


class TestClassUtils(TestCase):
    def test_get_prefix_name(self):
        class_name = 'UserViewSet'
        prefix = class_tools.get_class_prefix_name(class_name)
        self.assertEqual(prefix, 'User')
        
    def test_get_model_by_class_name(self):
        class_name = 'UserViewSet'
        prefix = class_tools.get_class_prefix_name(class_name)
        kls = class_tools.get_class_model(prefix)
        print(kls.name)
        self.assertIsNotNone(kls)
        self.assertIsNotNone(kls.name)

    def tet_get_serializer_by_class_name(self):
        class_name = 'UserViewSet'
        prefix = class_tools.get_class_prefix_name(class_name)
        kls = class_tools.get_class_serializer(prefix)
        self.assertIsNotNone(kls)
        self.assertIsNotNone(kls.name)
        

class TestSetClassService(TestCase):
    def test_set_service(self):
        class TestClass(object):
            model = None

        TestClass = class_tools.set_service(user_service)(TestClass)
#        self.assertIsNotNone(TestClass.model)
#        self.assertIsNotNone(TestClass.queryset)
       

class TestR(TestCase):
    def test_R(self):
        r = response.R()
        self.assertEqual(r.response['status'], 200)
        self.assertEqual(r.response['request'], 'success')

        error_code = 410000
        self.assertRaises(TypeError, r.set_response_error, error_code)

        error_code = 41020
        r.set_response_error(error_code)
        self.assertEqual(r.response['status'], 200)
        self.assertEqual(r.response['request'], 'fail')
        self.assertEqual(r.response['errors']['code'], 41020)
        self.assertTrue(isinstance(r.response['errors']['message'], str))

        self.assertIsNotNone(response.APIResponse(error_code))

        r = response.R()
        data = {'user': 'test'}
        r.set_response_data(data)
        self.assertEqual(r.response['data'], data)
        self.assertIsNotNone(response.APIResponse(data))



        
