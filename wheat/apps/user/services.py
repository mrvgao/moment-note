# -*- coding:utf-8 -*-

from django.db import transaction
from django.contrib.auth import authenticate, login

from customs.services import BaseService
from customs.response import Result
from errors import codes
from .models import User, AuthToken, FriendShip, Captcha
from .serializers import UserSerializer, AuthTokenSerializer, CaptchaSerializer
import datetime
from django.db.models import Q
from utils import utils
from customs.services import MessageService


class UserService(BaseService):

    model = User
    serializer = UserSerializer

    def register(self, phone, password, request=None, **kwargs):
        user = None
        if not self.check_if_registed(phone):
            user = self.create(phone, password, **kwargs)
        
        if user and request:  # if user created and request valid
            self.login_user(request, phone, password)
            new_token = AuthService.get_token(user.id)
            user.token.token = new_token

        return self.serialize(user)

    def delete(self, user_id):
        user = self.get(id=user_id)
        if user:
            user = super(UserService, self).delete(user)
        return user
            
    def create(self, phone, password, **kwargs):
        kwargs['password'] = password
        kwargs['phone'] = phone
        user = super(UserService, self).create(**kwargs)
        user.set_password(password)
        return user

    def set_password_by_phone_and_password(self, phone, password):
        user = self.get(phone=phone)
        self.set_password(user, password)
        return self.serialize(user)

    def set_password(self, user, password):
        user.set_password(password)
        user.save()
        return user

    def check_if_registed(self, phone, password=''):
        return self.exist(phone=phone)
    
    def login_user(self, request, phone, password):
        user = authenticate(username=phone, password=password)
        code = None
        if user:
            if user.activated:
                login(request, user)
                UserService.set_session_user_id(request, user.id)
                AuthService.refresh_token(user_id=user.id)
            else:
                code = codes.INACTIVE_ACCOUNT
        else:
            code = codes.INCORRECT_CREDENTIAL

        return code, self.serialize(user)

    def update_by_id(self, user_id, **kwargs):
        new_user = super(UserService, self).update_by_id(user_id, **kwargs)
        return self.serialize(new_user)

    @transaction.atomic
    def lazy_delete_user(self, user):
        user = self.update(user, deleted=True)
        return user

    @staticmethod
    def set_session_user_id(request, user_id):
        '''
        Set session user id. When user login or created.
        '''
        request.session.setdefault('user_id', user_id)

    @staticmethod
    def check_auth_token(user_id, token):
        token_obj = AuthToken.objects.get_or_none(user_id=user_id)
        if token_obj and token_obj.key == token and not token_obj.expired():
            return True
        return False

    @transaction.atomic
    @staticmethod
    def refresh_auth_token(token):
        token = AuthToken.objects.refresh_token(token)
        return token

    @transaction.atomic
    @staticmethod
    def create_friendship(user_a, user_b):
        friendship = None

        if user_a == user_b:
            friendship = None
        else:
            if user_a > user_b:
                user_a, user_b = user_b, user_a

            friendship, created = FriendShip.objects.get_or_create(user_a=user_a, user_b=user_b)
        return friendship

    @transaction.atomic
    @staticmethod
    def create_friendships(user_id, friend_ids):
        friendships = []
        for friend_id in friend_ids:
            user_a, user_b = user_id, friend_id
            if user_a > user_b:
                user_a, user_b = user_b, user_a
                friendships.append(FriendShip(user_a=user_a, user_b=user_b))
        if friendships:
            FriendShip.objects.bulk_create(friendships)
        return friendships

    @transaction.atomic
    @staticmethod
    def delete_friendship(user_id, user_2_id):
        user_a_b = Q(user_a=user_id, user_b=user_2_id)
        user_b_a = Q(user_a=user_2_id, user_b=user_id)
        condition = user_a_b | user_b_a
        friends = FriendShip.objects.filter(condition)
        for f in friends:
            f.delete()
        return True

    @staticmethod
    def get_user_friend_ids(user_id):
        friend_ids = []
        ids = FriendShip.objects.filter(user_a=user_id, deleted=False).values_list('user_b', flat=True)
        for id in ids:
            friend_ids.append(str(id))
            ids = FriendShip.objects.filter(user_b=user_id, deleted=False).values_list('user_a', flat=True)
        for id in ids:
            friend_ids.append(str(id))
        return friend_ids

    def update_avatar(self, user_id, avatar):
        user = self.get(id=user_id)
        self.update(user, avatar=avatar)
        return {'user_id': user_id, 'avatar': avatar}

    @staticmethod
    def is_friend(user_a, user_b):
        friend = True
        if user_a is None or user_b is None:
            friend = True
        elif str(user_a) == str(user_b):
            friend = True
        elif not UserService.exist_friendship(user_a, user_b):
            friend = False

        return friend

    @staticmethod
    def exist_friendship(user1, user2):
        exist = True
        if len(FriendShip.objects.filter(user_a=user1, user_b=user2)) == 0:
            if len(FriendShip.objects.filter(user_a=user2, user_b=user1)) == 0:
                exist = False
        return exist

    @staticmethod
    def all_is_friend(user_list):
        for u1 in user_list:
            for u2 in user_list:
                if not UserService.is_friend(u1, u2):
                    return False
        return True


class CapthchaService(BaseService):
    model = Captcha
    serializer = CaptchaSerializer

    def send_captcha(self, phone, send=True):
        send_succeed, code = MessageService.send_message(phone=phone, send=send)
        return send_succeed, code

    def check_captcha(self, phone, captcha):
        match = MessageService.check_captcha(phone=phone, captcha=captcha)
        return match


class AuthService(BaseService):
    model = AuthToken
    serializer = AuthTokenSerializer

    @staticmethod
    def check_if_token_valid(token):
        auth_token = AuthToken.objects.get_or_none(key=token)

        if auth_token:
            expired_time = auth_token.expired_at
            return expired_time > datetime.datetime.now()
        else:
            return False

    @staticmethod
    def refresh_token(user_id):
        token = AuthToken.objects.get_or_none(user_id=user_id)
        token = AuthToken.objects.refresh_token(token)
        return token

    @staticmethod
    def get_token(user_id):
        token = AuthToken.objects.get_or_none(user_id=user_id)
        return token.key

    @staticmethod
    def check_register_info_valid(phone, password):
        return utils.valid_phone(phone) and utils.valid_password(password)


user_service = UserService()
captcha_service = CapthchaService()
auth_service = AuthService()
