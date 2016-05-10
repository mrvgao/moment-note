'''
Delegates for service <==> api.

@Author Minchiuan Gao <2016-March-5>
'''

from api_tools import get_api_method


class Delegate(object):
    def __init__(self, surrogate, serialize_func=None):
        self.__surrogate = surrogate
        self._set_methods(self._collect_methods(), serialize_func)

    def __test_method_callable(self, method_name):
        if not method_name.startswith('__') and callable(getattr(self.__surrogate, method_name)):
            return True
        return False

    def _collect_methods(self):
        callable_methods = filter(self.__test_method_callable, dir(self.__surrogate))
        return callable_methods

    def _set_methods(self, callable_methods, serialize_func=None):
        def set_methods(method_name):
            method = getattr(self.__surrogate, method_name)
            if getattr(method, '__api__', False):  # default get none is false
                method = get_api_method(method, serialize_func)
            setattr(self, method_name, method)
            
        map(set_methods, callable_methods)
        
        
def delegate(cls, serialize_func=None):
    return Delegate(cls, serialize_func)
    
