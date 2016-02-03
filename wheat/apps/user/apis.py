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
from .permissions import admin_required, is_userself
from .validators import check_request
from .services import UserService


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
    def update(self, request, id, *args, **kwargs):
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
    def destroy(self, request, id, *args, **kwargs):
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

    @list_route(methods=['post'])
    def token(self, request):
        '''
        Get token(old or new) by phone and password or refresh old token.
        ### Example Request

            {
                "phone": "18582227569",
                "password": "q1w2e3",
                "token": "old token"
            }
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body
        '''
        key = request.data.get('token', '')
        if key:
            token = UserService.get_auth_token(key=key)
            if token:
                token = UserService.refresh_auth_token(token)
                return SimpleResponse(token.token)
            else:
                return SimpleResponse(code=codes.INVALID_TOKEN)
        phone = request.data.get('phone', '')
        password = request.data.get('password', '')
        result = UserService.login_user(request, phone, password)
        if result.success:
            return SimpleResponse(result.data.token)
        else:
            return SimpleResponse(errors=result.errors)
        return SimpleResponse(success=False)


class InvitationViewSet(ListModelMixin,
                        viewsets.GenericViewSet):
    pass
