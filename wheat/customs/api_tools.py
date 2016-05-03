'''
Add information of apis

@Author Minchiuan Gao (2016-4-28)
'''
import inspect
import sys


def _get_file_name(frame):
    return frame[1]


def called_by_target_file(caller_file_name, stack):
    called = False
    python_system_file = sys.prefix
    for f in stack:
        file_name = _get_file_name(f)
        if file_name.startswith(python_system_file):
            break
        elif file_name.endswith(caller_file_name):
            called = True
            break
    return called

        
def api(func):
    '''
    Changes func's return value.
    If func is been called in apis.py file,
    the func's return value will changet to serialized value.
    else, will not change the return value of this func.
    '''
    # target_file = '/apis.py'

    # stack = inspect.stack(0)

    is_cls = isinstance(func, classmethod)
    is_static = isinstance(func, staticmethod)

    if is_static:
        raise TypeError('Not Support Staticmethod for @api decorator,' + func.__func__.__name__)

    # called = called_by_target_file(target_file, stack)

    if is_cls:
        new_func = change_func_return_value(func.__func__)
        func = classmethod(new_func)
    #        func.__func__.__dict__.setdefault('called', True)
    else:
        new_func = change_func_return_value(func)
        func = new_func
    #        func.__dict__.setdefault('called', True)

    return func


def get_class_that_defined_method(meth):
    for cls in inspect.getmro(meth.im_class):
        if meth.__name__ in cls.__dict__:
            return cls
        return None


def change_func_return_value(func):
    def change_value(arg, *args, **kwargs):

        serialize_func = None
        if type(func).__name__ == 'function':
            cls = arg
        else:  # func is instancemethod.
            cls = get_class_that_defined_method(func)

        value = func(arg, *args, **kwargs)

        if value and hasattr(cls, 'serialize'):  # if value is not None
            if hasattr(cls, '__call__'):
                serialize_func = cls().serialize
            else:
                serialize_func = cls.serialize

            try:
                serialized_data = serialize_func(value)
                setattr(value, 'serialized_data', serialized_data)
            except Exception as e:
                print e
                print('{0} not support serialize'.format(value))
        return value
    return change_value


class ReturnMap(object):
    pass

def get_return_value(return_map):
    results = filter(lambda cond: cond, return_map)
    result = return_map[results[0]]
    return result

    
