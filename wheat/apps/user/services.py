# -*- coding:utf-8 -*-

from django.db import transaction
from django.contrib.auth import authenticate, login

from customs.services import BaseService
from customs.response import Result
from errors import codes
from .models import User, AuthToken
from .serializers import UserSerializer, AuthTokenSerializer


UserUpdateFields = ('phone', 'nickname', 'first_name', 'last_name', 'avatar',
                    'tagline', 'gender', 'city', 'province', 'country')


class UserService(BaseService):

    @classmethod
    def _get_model(cls, name='User'):
        if name == 'User':
            return User
        elif name == 'AuthToken':
            return AuthToken

    @classmethod
    def get_serializer(cls, model='User'):
        if model == 'User':
            return UserSerializer
        elif model == 'AuthToken':
            return AuthTokenSerializer

    @classmethod
    def serialize(cls, obj, context={}):
        if isinstance(obj, User):
            return UserSerializer(obj, context=context).data
        elif isinstance(obj, AuthToken):
            return AuthTokenSerializer(obj, context=context).data

    @classmethod
    def is_logged_in(cls, user):
        return isinstance(user, UserService._get_model())

    @classmethod
    def get_user(cls, **kwargs):
        return User.objects.get_or_none(**kwargs)

    @classmethod
    def get_users(cls, **kwargs):
        return User.objects.filter(**kwargs)

    @classmethod
    @transaction.atomic
    def create_user(cls, phone='', password='', **kwargs):
        user = UserService.get_user(phone=phone)  # phone is unique
        if user:
            return user
        user = User.objects.create_user(phone, password)
        if kwargs:
            UserService.update_user(user, **kwargs)
        return user

    @classmethod
    @transaction.atomic
    def update_user(cls, user, **kwargs):
        for field in UserUpdateFields:
            if field in kwargs:
                setattr(user, field, kwargs[field])
        user.save()
        return user

    @classmethod
    @transaction.atomic
    def lazy_delete_user(cls, user):
        if user:
            user.update(deleted=True)
            return True
        return False

    @classmethod
    def login_user(cls, request, phone, password):
        user = authenticate(username=phone, password=password)
        if user:
            if user.activated:
                login(request, user)
                return Result(data=user)
            else:
                return Result(code=codes.INACTIVE_ACCOUNT)
        else:
            return Result(code=codes.INCORRECT_CREDENTIAL)

    @classmethod
    def get_auth_token(cls, **kwargs):
        return AuthToken.objects.get_or_none(**kwargs)

    @classmethod
    @transaction.atomic
    def refresh_auth_token(cls, token):
        token = AuthToken.objects.refresh_token(token)
        return token
