from django.test import TestCase
from customs.urls import get_urlpattern
from customs.urls import get_url
from customs import class_tools

import sys


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
        
