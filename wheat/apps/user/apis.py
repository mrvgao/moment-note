# -*- coding:utf-8 -*-
from rest_framework import viewsets, status
from rest_framework.decorators import list_route, detail_route

from customs.response import SimpleResponse
from customs.response import APIResponse
from customs.viewsets import ListModelMixin
from errors import codes
from .permissions import admin_required, login_required
from .permissions import user_is_same_as_logined_user
from .permissions import check_token
from .services import AuthService
from customs import class_tools
from apps.user.services import user_service
from apps.user.services import captcha_service
from apps.user.services import auth_service
from django.contrib.auth import login, authenticate


@class_tools.set_filter(['phone'])
@class_tools.set_service(user_service)
class UserViewSet(ListModelMixin,
                  viewsets.ModelViewSet):

    """
    麦粒用户系统相关API.
    ### Resource Description
    """

    @list_route(methods=['get'])
    def register(self, request):
        '''
        测试该用户是否已经被注册
        ### Request example:
        URL: {API_URL}/users/register?phone=18582227569

        phone -- phone number
        ---
        omit_serializer: true
        '''
        PHONE = 'phone'
        phone = request.query_params.get(PHONE, None)

        registed = user_service.check_if_registed(phone)

        status_code = 200
        if registed:
            status_code = 409

        data = {
            'phone': phone,
            'registered': registed
        }

        return APIResponse(data, status=status_code)

    @list_route(methods=['post'])
    @login_required
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
        password = request.data.get('password', None)

        user = user_service.set_password_by_phone_and_password(phone, password)

        status_code = 406 if not user else None

        result = user or codes.PHONE_NUMBER_NOT_EXIST

        return APIResponse(result, status=status_code)
        
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
        phone = request.data.pop('phone', None)[0]
        password = request.data.pop('password', None)[0]

        user = None
        error_code = None

        valid, registed_again = user_service.check_register_info(phone, password)

        status_code = 200

        if not valid:
            error_code = codes.INVALID_REG_INFO
            status_code = 400
        elif registed_again:
            error_code = codes.PHONE_ALREAD_EXIST
            status_code = 409
        else:
            user = user_service.register(phone, password)
            login(request, authenticate(username=phone, password=password))

        return_value = user or error_code
        # if user is None, return error code  r = u | code

        return APIResponse(return_value, status=status_code)

    @admin_required
    def destroy(self, request, id):
        '''
        Delete user, requiring admin permission
        ---
        omit_serializer: true
        '''
        return APIResponse(user_service.delete(user_id=id))

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

        user = user_service.login_user(phone, password)
        if user:
            login(request, authenticate(username=phone, password=password))
            return APIResponse(user)
        else:
            error_code = codes.INCORRECT_CREDENTIAL
            return APIResponse(error_code, status=401)

    @login_required
    @user_is_same_as_logined_user
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
        avatar = request.data.get('avatar', None)
        user = user_service.update_by_id(request.user.id, avatar=avatar)
        return APIResponse(user)


@class_tools.set_service(captcha_service)
class CaptchaViewSet(viewsets.ViewSet):

    lookup_url_kwarg = 'phone'

    @check_token
    def retrieve(self, request, phone):
        '''
        获得某个手机号的验证码

        ### Example Request

        captcha/{phone}/

        ### Response

        {
            'phone': phone,
            'captcha': code,
        }

        '''
        code = captcha_service.get_captch(phone)

        response = {
            'phone': phone,
            'captcha': code,
        }

        return APIResponse(response)

    @check_token
    @detail_route(methods=['get'])
    def send(self, request, phone):
        '''
        Does actions for captcha.
        captcha/{phone}/send/

        发送验证码

        {
            'phone': phone,
            'captcha': code,
        }

        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: phone
              paramType: body
        '''

        phone_valid = user_service.check_phone_valid(phone)

        if phone_valid:
            code = captcha_service.get_captch(phone)
            send_succeed = captcha_service.send_captcha(phone=phone, captcha=code)
            response = {
                'phone': phone,
                'captcha': code
            }
        else:
            send_succeed = False

        if send_succeed:
            return APIResponse(response)
        else:
            return APIResponse(codes.CAPTCHA_SEND_FAILED, status=408)


@class_tools.set_service(auth_service)
class TokenViewSet(viewsets.ViewSet):

    lookup_url_kwarg = 'code'

    @user_is_same_as_logined_user
    @login_required
    @list_route(methods=['put'])
    def refresh(self, request):
        '''
        ### Example Request

            {
                "user_id": "user_id",
                "token": "old token"
            }
        '''
        uid = str(request.user.id)
        token = auth_service.refresh_user_token(uid)
        return APIResponse({'user_id': uid, 'new_token': token})

    @login_required
    @detail_route(methods=['get'])
    def valid(self, request, code):
        '''
        GET: check token if valid.

        ## Example Request:

            {URL}/token/{code}/valid/
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body

        '''
        valid = auth_service.check_auth_token(request.user.id, code)
        data = {'valid': valid}
        return SimpleResponse(data)
