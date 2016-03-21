# -*- coding:utf-8 -*-

from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions, viewsets, status
from rest_condition import Or
from rest_framework.decorators import list_route

from customs.permissions import AllowPostPermission
from customs.response import SimpleResponse
from customs.viewsets import ListModelMixin
from errors import codes
from utils import utils
from .permissions import admin_required, is_userself, login_required
from .validators import check_request
from .services import UserService, AuthService
from customs.services import MessageService


class UserViewSet(ListModelMixin,
                  viewsets.GenericViewSet):

    """
    麦粒用户系统相关API.
    ### Resource Description
    """
    model = UserService._get_model()
    queryset = model.get_queryset()
    serializer_class = UserService.get_serializer()
    lookup_field = 'id'
    permission_classes = [
        Or(permissions.IsAuthenticatedOrReadOnly, AllowPostPermission,)]
    filter_fields = ['phone']

    @admin_required
    def list(self, request):
        '''
        List all users by pages. Admin Required.
        page -- page
        ---
        omit_serializer: true
        '''

        response = super(UserViewSet, self).list(request)
        return SimpleResponse(response.data)

    @list_route(methods=['get'])
    def register(self, request):
        '''
        获取关于注册列表的相关信息

        ### Request example:

        URL: {API_URL}/users/register?phone=18582227569 

        phone -- phone number
        ---
        omit_serializer: true 
        '''
        PHONE = 'phone'
        phone = request.query_params.get(PHONE, None)
        if phone:
            return self._check_if_registed(phone)
        else:
            return SimpleResponse(errors='query_params not support')


    def _check_if_registed(self, phone):
        user = UserService.get_users(phone=phone)

        context = {
            "phone": phone,
            "registered": False
        }

        if len(user) != 0:
            context['registered'] = True

        return SimpleResponse(context)

    @list_route(methods=['post'])
    def password(self, request):
        '''
        修改用户的密码，用于重置密码

        ###Example Reqeust

        {
            "phone": "18582227569",
            "password": "12345678"
        }
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body
        '''
        
        phone = request.data.get('phone', None)
        user = UserService.get_user(phone=phone)
        return self._update_user_info(user, request.data)
        
    def _update_user_info(self, user, data):
        if not user:
            return SimpleResponse(errors=codes.errors(codes.USER_NOT_EXIST))
        success = UserService.update_user(user, **data)
        if success:
            data = UserService.serialize(user)
            return SimpleResponse(data)
        return SimpleResponse(success=False)

    def create(self, request):
        '''
        Registration.
        ### Request Example

            {
                "phone": "xxx",
                "password": "123456"
                ...and update fields...
            }
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body
        '''

        phone = request.data.pop('phone', None)
        password = request.data.pop('password', None)
        if not phone or not password:
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST)
        if not utils.valid_phone(phone) or not utils.valid_password(password):
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST)
        user = UserService.get_user(phone=phone)
        if user:
            return SimpleResponse(status=status.HTTP_409_CONFLICT)
        user = UserService.create_user(phone=phone, password=password, **request.data)
        data = UserService.serialize(user)
        UserService.login_user(request, phone, password)
        return SimpleResponse(data)

    @check_request('user')
    def retrieve(self, request, id):
        '''
        Retrieve user profile and other info. info is limited for not logged in user
        ---
        omit_serializer: true
        '''
        data = UserService.serialize(request.user)
        if isinstance(request.user, AnonymousUser) or request.user.id != data['id']:
            user_self = False
        else:
            user_self = True

        def _retrieve(self, request, id):
            if not user_self:
                # UserService.get_restricted_account_info(data)
                pass
            return SimpleResponse(data)
        return _retrieve(self, request, id)

    @is_userself
    def update(self, request, id):
        '''
        Update user info
        ### Example Request

            {
                "phone": "xxx",
                "nickname": "xxx",
                "first_name": "xxx",
                "last_name": "xxx",
                "tagline":"xxx",
                "gender": "M/F",
                "marital_status": true/false,
                "birthday": "xxx",
                "city": "xxx",
                "province": "xxx",
                "country": "xxx",
            }
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body
        '''
        user = UserService.get_user(id=id)
        if not user:
            return SimpleResponse(errors=codes.errors(codes.USER_NOT_EXIST))
        success = UserService.update_user(user, **request.data)
        if success:
            data = UserService.serialize(user)
            return SimpleResponse(data)
        return SimpleResponse(success=False)

    @admin_required
    def destroy(self, request, id):
        '''
        Delete user, requiring admin permission
        ---
        omit_serializer: true
        '''
        user = UserService.get_user(id=id)
        return SimpleResponse(success=UserService.lazy_delete_user(user))

    @list_route(methods=['post'])
    def login(self, request):
        '''
        User login, return user info if success
        ### Example Request

            {
                "phone": "18582227569",
                "password": "q1w2e3"
            }
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body
        '''
        phone = request.data.get('phone', '')
        password = request.data.get('password', '')
        result = UserService.login_user(request, phone, password)

        if result.success:
            data = UserService.serialize(result.data, context={'request': request})
            return SimpleResponse(data)
        return SimpleResponse(errors=result.errors)

    @login_required
    @list_route(methods=['put', 'get'])
    def token(self, request):
        '''
        1. put: refresh old token.
        2. GET: check token if valid.
        ### Example Request

        When POST:


            {
                "user_id": "user_id",
                "token": "old token"
            }

        2. GET: 获得关于某个token的信息

        When GET:

            {URL}/user/token/?action=check&token=XXX

        token -- token, 仅当Get时使用
        action -- 仅当Get时使用，对token采取的操作，当action == check 时候，返回该token是否有效

        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body

        '''

        USER_ID, TOKEN = 'user_id', 'token'
        if request.method == 'PUT':
            user_id = request.data.get(USER_ID)
            key = request.data.get(TOKEN, None)
            if not key:
                return SimpleResponse(code=codes.INVALID_TOKEN)
            elif str(user_id) != str(request.user.id):
                return SimpleResponse(code=codes.LOGIN_REQUIRED)
            else:
                token = UserService.get_auth_token(key=key)
                if token:
                    token = UserService.refresh_auth_token(token)
                    return SimpleResponse(token.token)
                else:
                    return SimpleResponse(code=codes.INVALID_TOKEN)
        elif request.method == 'GET':
            TOKEN, VALID = 'token', 'valid'
            token = request.query_params.get(TOKEN, None)
            data = {VALID: False}

            data[VALID] = AuthService.check_if_token_valid(token)
            return SimpleResponse(data)

    @login_required
    @list_route(methods=['put'])
    def avatar(self, request):
        '''
        修改用户的头像信息

        ### Example Request:

            {
                "avatar": "new avatar url",
                "user_id": "the id of the updated user"
            }
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: data
              paramType: body
        '''

        UESR_ID, AVATAR = 'user_id', 'avatar'

        user_id = request.data.get(UESR_ID, None)
        avatar = request.data.get(AVATAR, None)

        if user_id != str(request.user.id):
            return SimpleResponse(errors='user id != logined user')
        elif not avatar:
            return SimpleResponse(errors='avatar value cannot be null')
        else:
            data = UserService.update_avatar(user_id, avatar)
            return SimpleResponse(data)

    @list_route(methods=['get'])
    def online(self, request):
        '''
        测试该user_id是否正保持在线，保持在线是指，该client登录之后，session没有中断

        返回样例：

        online ＝ ｛
            “online”： False
        ｝

        该用户未在此session登录

        user_id -- user_id
        ---
        omit_serializer: true
        '''
        online = {
            "online": False
        }

        user_id = request.query_params.get('user_id', None)

        if request.session.get('user_id', None) == user_id:
            online['online'] = True

        return SimpleResponse(online)

    @list_route(methods=['post'])
    def captcha(self, request):
        '''
        Does actions for captcha.

        用以处理和验证码相关的信息，根据action不同，可以有
        1. 发送验证码（action = send），
        2. 测试发送验证码但是不发送短信（action ＝ test_send）
        3. 检查验证码是否相符（action = check）
        ### Example Request

            {
                "phone": "18582227569"
                // 该请求为发送验证码时候的请求
            }

            {
                 "phone": "18857453090",
                 "captcha": "259070"
                 // 该请求为检查验证码是否相符时候的请求
            }

        action -- action
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: phone
              paramType: body
        '''

        ACTION, PHONE, CAPTCHA = 'action','phone', 'captcha'
        SEND, CHECK, TEST_SEND = 'send', 'check', 'test_send'
        action = request.query_params.get(ACTION, None)
        if action == SEND:
            phone = request.data.get(PHONE, None)
            return self._send_message(phone, send=True)
        elif action == TEST_SEND:
            phone = request.data.get(PHONE, None)
            return self._send_message(phone, send=False)
        elif action == CHECK:
            phone = request.data.get(PHONE, None)
            captcha = request.data.get(CAPTCHA, None)
            return self._check_captcha(phone, captcha)
        else:
            return SimpleResponse(errors='action not supply')

    def _check_captcha(self, phone, captcha):
        match = MessageService.check_captcha(phone=phone, captcha=captcha)
        return_context = {
            'phone': phone,
            'captcha': captcha,
            'matched': False
        }

        if match:
            return_context['matched'] = True

        return SimpleResponse(return_context)

    def _send_message(self, phone, send):
        send_succeed, code = MessageService.send_message(phone=phone, send=send)

        return_context = {
            'phone': phone,
            'captcha': code
        }

        if not send_succeed:
            return SimpleResponse(success=False)
        else:
            return SimpleResponse(return_context)


class InvitationViewSet(ListModelMixin,
                        viewsets.GenericViewSet):
    pass
