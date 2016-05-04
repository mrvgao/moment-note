from django.test import TestCase
from services import UserService
from customs.api_tools import api
from customs.api_tools import get_return_value
from apis import Caller


class APIFuncTest(TestCase):
    #def test_add_serialized_data(self):
        #user_service = UserService()
        #decorated_func = api(user_service.test_add)
        #result = decorated_func(1, 2)
        #self.assertTrue(hasattr(result, 'serialized_data'))
        #self.assertEqual(result.num, 1+2)

    #def test_decorator(self):
        #pass
        #result = UserService().decorator(1, 2)
        #self.assertTrue(hasattr(result, 'serialized_data'))
        #self.assertEqual(result.num, 1+2)

    def test_change_value(self):
        result = UserService().test(1, 1)
        changed_result = Caller().test_method(1, 1)
        self.assertNotEqual(result, changed_result)


class TestReturnVlaue(TestCase):
    def test_get_return_value(self):
        register = True
        valid = True

        return_map = {
            register: 'You have registed',
            not valid: 'Info is not valid',
            not register and valid: 'Registed succeed'
        }

        result = get_return_value(return_map)
        self.assertEqual(result, return_map[register])

        register = False
        valid = False

        return_map = {
            register: 'You have registed',
            not valid: 'Info is not valid',
            not register and valid: 'Registed succeed'
        }

        result = get_return_value(return_map)
        self.assertEqual(result, return_map[not valid])

        register = False
        valid = True

        return_map = {
            register: 'You have registed',
            not valid: 'Info is not valid',
            not register and valid: 'Registed succeed'
        }

        result = get_return_value(return_map)
        self.assertEqual(result, return_map[not register and valid])


