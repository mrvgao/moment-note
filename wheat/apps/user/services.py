# -*- coding:utf-8 -*-

from django.db import transaction
from django.contrib.auth import authenticate, login

from customs.services import BaseService
from customs.response import Result
from .models import User, AuthToken, FriendShip, Captcha
from .serializers import UserSerializer, AuthTokenSerializer, CaptchaSerializer
from .serializers import FriendshipSerializer
import datetime
from django.db.models import Q
from utils import utils
from customs.services import MessageService
from customs.api_tools import api


class UserService(BaseService):

    model = User
    serializer = UserSerializer

    @api
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
        user.save()
        return user

    @api
    def set_password_by_phone_and_password(self, phone, password):
        user = self.get(phone=phone)
        if user:
            self.set_password(user, password)
        return user

    def set_password(self, user, password):
        user.set_password(password)
        user.save()
        return user

    def check_if_registed(self, phone, password=''):
        return self.exist(phone=phone)
    
    @api
    def update_by_id(self, user_id, **kwargs):
        new_user = super(UserService, self).update_by_id(user_id, **kwargs)
        return new_user

    @transaction.atomic
    @api
    def lazy_delete_user(self, user):
        user = self.update(user, deleted=True)
        return user

    def check_register_info(self, phone, password):
        valid_info = self.check_info_formatted(phone, password)
        registed_again = self.check_if_registed(phone)
        return valid_info, registed_again

    @api
    def register(self, phone, password, **kwargs):
        user = None

        if not self.check_if_registed(phone):
            user = self.create(phone, password, **kwargs)
            user = authenticate(username=phone, password=password)
            
        return user

    def check_info_formatted(self, phone, password):
        PHONE_LENGTH = 11
        PWD_LENGTH = 6
        return len(phone) == PHONE_LENGTH and len(password) >= PWD_LENGTH

    def check_if_credential(self, phone, password):
        user = authenticate(username=phone, password=password)
        if user:
            return True
        return False

    def check_if_activated(self, phone):
        user = self.get(phone=phone)
        if user:
            return user.activated
        else:
            return False

    @api
    def login_user(self, phone, password):
        user = authenticate(username=phone, password=password)
        return user


class FriendshipService(BaseService):
    model = FriendShip
    serializer = FriendshipSerializer

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

    @staticmethod
    def is_friend(user_a, user_b):
        friend = True
        if user_a is None or user_b is None:
            friend = True
        elif str(user_a) == str(user_b):
            friend = True
        elif not FriendshipService.exist_friendship(user_a, user_b):
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
                if not FriendshipService.is_friend(u1, u2):
                    return False
        return True


class CapthchaService(BaseService):
    model = Captcha
    serializer = CaptchaSerializer

    def _expired(self, captcha_obj):
        VALID_MIN = 10
        valid_time = 60 * VALID_MIN
        # valid time is 10 mins.
        
        created_time = captcha_obj.created_at
        if (datetime.datetime.now() - created_time).seconds > valid_time:
            return True
        return False
        
    def get_new_captch(self, phone):
        captcha_code = MessageService.random_code(phone, plus=datetime.datetime.now().microsecond)
        return captcha_code

    def get_captcha_code_from_obj(self, captcha_obj):
        captcha_code = captcha_obj.code

        if self._expired(captcha_obj):
            captcha_code = self.get_new_captch(captcha_obj.phone)
            self.update(captcha_obj, code=captcha_code)

        return captcha_code

    def get_captch(self, phone):
        captcha_obj = self.get(phone=phone)
        captcha_code = None
        if captcha_obj:
            captcha_code = self.get_captcha_code_from_obj(captcha_obj)
        else:
            captcha_code = self.get_new_captch(phone)
            self.create(phone=phone, code=captcha_code)

        return captcha_code

    def send_captcha(self, phone, send=True):
        send_succeed, code = MessageService.send_message(phone=phone, send=send)
        return send_succeed, code

    def check_captcha(self, phone, captcha):
        captcha_obj = self.get(phone=phone, code=captcha)
        if captcha_obj:
            return True
        return False


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
    def refresh_token(user_id, refresh_token=True):
        token = AuthToken.objects.get_or_none(user_id=user_id)
        if refresh_token:
            token = AuthToken.objects.refresh_token(token)
        return token

    @staticmethod
    def get_token(user_id):
        token = AuthToken.objects.get_or_none(user_id=user_id)
        return token.key

    @staticmethod
    def check_auth_token(user_id, token):
        token_obj = AuthToken.objects.get_or_none(user_id=user_id)
        if token_obj and token_obj.key == token and not token_obj.expired():
            return True
        return False


user_service = UserService()
captcha_service = CapthchaService()
auth_service = AuthService()
