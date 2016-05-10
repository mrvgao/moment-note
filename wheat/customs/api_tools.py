'''
Add information of apis

@Author Minchiuan Gao (2016-4-28)
'''
import inspect
import sys
import functools


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
    setattr(func, '__api__', True)
    return func


def get_api_method(func, serialize_func=None):
    '''
    Changes func's return value.
    If func is been called in apis.py file,
    the func's return value will changet to serialized value.
    else, will not change the return value of this func.
    '''

    is_cls = isinstance(func, classmethod)
    is_static = isinstance(func, staticmethod)

    if is_static:
        raise TypeError('Not Support Staticmethod for @api decorator,' + func.__func__.__name__)

    if is_cls:
        new_func = change_func_return_value(func.__func__, serialize_func)
        func = classmethod(new_func)
    else:
        new_func = change_func_return_value(func, serialize_func)
        func = new_func

    return func


def get_class_that_defined_method(meth):
    for cls in inspect.getmro(meth.im_class):
        if meth.__name__ in cls.__dict__:
            return cls
        return None


def change_func_return_value(func, serialize_func=None):
    @functools.wraps(func)
    def change_value(arg, *args, **kwargs):
        try:
            value = func(arg, *args, **kwargs)
            value = serialize_func(value)
        except Exception as e:
            print e
            print('lack of defining serialize func of {0}'.format(func.__name__))

        return value
    return change_value


class ReturnMap(object):
    pass


def get_return_value(return_map):
    results = filter(lambda cond: cond, return_map)
    result = return_map[results[0]]
    return result

    
