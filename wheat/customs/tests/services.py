from customs.api_tools import api
from customs.services import BaseService
from apps.user.models import User
from apps.user.serializers import UserSerializer


class Num(object):
    def __init__(self, num):
        self.num = num

        
class UserService(BaseService):
    name = 'UserService'

    model = User
    serrializer = UserSerializer

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


user_service = UserService()
