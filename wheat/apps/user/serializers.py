# -*- coding:utf-8 -*-

from customs.serializers import XModelSerializer
from customs.fields import XImageField
from .models import User, AuthToken


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
                  'is_admin', 'activated', 'activated_at',
                  'created_at', 'updated_at', 'last_login')


class AuthTokenSerializer(XModelSerializer):

    class Meta:
        model = AuthToken
