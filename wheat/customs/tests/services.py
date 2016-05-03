from customs.api_tools import api


class Num(object):
    def __init__(self, num):
        self.num = num

        
class UserService(object):
    name = 'UserService'

    @api
    def test(self, num1, num2):
        return num1 + num2

    @api
    @classmethod
    def test_cls(cls, num1):
        return num1 + 10

    @staticmethod
    def test_static(name):
        return 0

    @api
    def decorator(self, num, num2):
        return Num(num + num2)

    def test_add(self, num1, num2):
        return Num(num1 + num2)

    def serialize(self, value):
        return True
