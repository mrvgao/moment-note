# -*- coding:utf-8 -*-

from customs.serializers import XModelSerializer
from customs.fields import XImageField
from rest_framework.serializers import BooleanField
from .models import User, AuthToken, Captcha
from rest_framework import serializers


class UserSerializer(XModelSerializer):
    avatar = XImageField(
        max_length=100,
        allow_empty_file=False,
        required=False,
        use_url=True,
        style={'input_type': 'file'})

    class Meta:
        model = User
        fields = ('id', 'phone', 'nickname', 'token',
                  'first_name', 'last_name', 'full_name',
                  'avatar', 'tagline', 'marital_status',
                  'gender', 'birthday', 'city',
                  'province', 'country', 'role',
                  'activated', 'updated_at', 'last_login')

        read_only_fields = ('activated', 'updated_at', 'last_login', 'password')


class AuthTokenSerializer(XModelSerializer):

    class Meta:
        model = AuthToken
        fields = ('key', 'user_id', 'created_at', 'expired_at')


class CaptchaSerializer(XModelSerializer):

    class Meta:
        model = Captcha
        fields = ('phone', 'code', 'created_at')

        
