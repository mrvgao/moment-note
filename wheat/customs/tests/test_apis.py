from django.test import TestCase
from services import user_service
from customs.api_tools import get_return_value
from services import user_service_delegate


class APIFuncTest(TestCase):
    def test_delegate(self):
        result = user_service_delegate.test(1, 2)
        result_org = user_service.test(1, 2)

        inner_call = user_service_delegate.test_inner_call(1)
        inner_call_result = user_service.test_inner_call(1)

        self.assertNotEqual(result, result_org)
        self.assertNotEqual(inner_call, inner_call_result)


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


