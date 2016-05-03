from services import UserService


class Caller(object):
    def test_cls(self):
        func = UserService.test_cls
        print UserService.test_cls(10)
        return func

    def test_method(self):
        func = UserService().test
        print UserService().test(1, 2)
        return func

    #def test_static(self):
    #    func = UserService.test_static
    #    print UserService.test_static('name')
    #    return func

if __name__ == '__name__':
    Caller().test_cls()
