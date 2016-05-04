from services import UserService
from services import user_service
from customs import class_tools


@class_tools.set_service(user_service)
class Caller(object):
    #def test_cls(self):
        #return_value = user_service.test_cls(10, 20)
        #print UserService.test_cls(10)
        #return func

    def test_method(self, num1, num2):
        value = user_service.test(num1, num2)
        return value

    #def test_static(self):
    #    func = UserService.test_static
    #    print UserService.test_static('name')
    #    return func

if __name__ == '__name__':
    Caller().test_cls()
