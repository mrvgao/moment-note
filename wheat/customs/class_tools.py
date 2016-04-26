'''
Class tools for django and restfulframework class.

@Author Minchiuan Gao (2016-4-21)
'''
from rest_framework import permissions
import inspect
import functools
from rest_condition import Or
from customs.permissions import AllowPostPermission


def set_service(service):
    def func(cls):
        try:
            cls.model = service.get_model()
            cls.serializer_class = service.get_serializer()
        except AttributeError as e:
            print('service without method get_model or get_serializer')
            raise e
        else:
            def serialize_data(cls, data, many=False):
                return cls.serializer_class(data, many=many).data

            cls.serialize_data = classmethod(serialize_data)
            cls.queryset = cls.model.get_queryset()
            cls.lookup_field = 'id'
            cls.permission_classes = [Or(permissions.IsAuthenticatedOrReadOnly, AllowPostPermission,)]
            return cls
    return func


def default_view_set(cls):
    '''
    Sets cls as follow:
    pre: if cls's name is TestClass
    1. cls.model <= Test, which is the prefix of class name
    2. cls.queryset <= Test.get_queryset(),
    3. cls.serializer_class <= TestSerializer
    4. cls.lookup_field <= 'id'
    5. cls.permission_classes <=[
        Or(permissions.IsAuthenticatedOrReadOnly, AllowPostPermission,)]
    '''
    cls_name = get_class_prefix_name(cls.__name__)  # get Class from ClassViewSet from class

    try:
        cls.model = get_class_model(cls_name)
        cls.serializer_class = get_class_serializer(cls_name)

        def serialize_data(cls, data, many=False):
            return cls.serializer_class(data, many=many).data

        cls.serialize_data = classmethod(serialize_data)

    except NameError as e:
        print e.message
        msg_1 =  'Keep your model name, serializer name and class name same'
        msg_2 =  'If not same, set model and serializer mannually'
        raise NameError(msg_1 + '\n' + msg_2 + '\n' + e.message)
    else:
        cls.queryset = cls.model.get_queryset()

    cls.lookup_field = 'id'
    cls.permission_classes = [Or(permissions.IsAuthenticatedOrReadOnly, AllowPostPermission,)]

    return cls


def set_model(model_name):
    def func(cls):
        model = get_class_model(model_name)
        cls.model = model
        cls.queryset = model.get_queryset()
        return cls
    return func


def set_serializer(serializer_name):
    def func(cls):
        serializer = get_class_serializer(serializer_name)
        cls.serializer_class = serializer
        return cls
    return func


def set_loopup_field(loop_up_field):
    pass


def set_filter(filter_fields):
    def func(cls):
        cls.filter_fields = filter_fields
        return cls
    return func


def set_permisson(permission_list):
    pass


def _get_caller_filename(current_frame):
    TARGET_API = 'apis.py'
    TEST_FILE = 'tests.py'  # for auto test
    current_filename = current_frame.f_code.co_filename
    if current_filename.endswith(TARGET_API) or current_filename.endswith(TEST_FILE):
        return current_frame.f_code.co_filename
    else:
        current_frame = current_frame.f_back
        return _get_caller_filename(current_frame)


def get_class_from_module(module_type, class_name):
    kls = None
    current_frame = inspect.currentframe()
    base_path = _get_caller_filename(current_frame)
    module_name = _get_module_name(base_path)

    module_type_func = {
        'models': lambda a: a,
        'serializers': lambda a: a + 'Serializer'
    }

    try:
        class_name = module_type_func[module_type](class_name)
        import_code = 'from %s .%s import %s' % (module_name, module_type, class_name)
        exec(import_code)
    except KeyError:
        raise NameError('unsupport ' + module_type + 'or cannot find ' + class_name)
    else:
        assign = 'kls = ' + class_name
        exec(assign)
        return kls


def _get_module_name(base_path):
    ROOT = 'wheat'
    base_path = base_path[base_path.rindex(ROOT):]
    # change ****/wheat/XXXX/apis.py
    # to wheat/XXXX/apis.py

    base_path = base_path[: base_path.rindex('.')]
    # change wheat/XXXX/apis.py to wheat/XXXX/apis

    base_path = base_path[: base_path.rindex('/')]
    # change wheat/XXXX/apis to wheat/XXXX

    module_name = base_path.replace('/', '.')
    # change wheat/XXXX to wheat.XXXX

    module_name = module_name.replace('wheat.', '')
    return module_name


def get_class_prefix_name(class_name):
    '''
    if class name is UserViewSet, return the User
    '''
    SPLIT = 'ViewSet'
    index = class_name.find(SPLIT)
    return class_name[:index]


MODELS, SERIALIZERS = 'models', 'serializers'


#  Get model by class name ###############
get_class_model = functools.partial(get_class_from_module, MODELS)


#  Get Serializer by class name ###############
get_class_serializer = functools.partial(get_class_from_module, SERIALIZERS)
