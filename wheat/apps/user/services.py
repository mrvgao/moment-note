# -*- coding:utf-8 -*-

from django.db import transaction
from django.contrib.auth import authenticate

from customs.services import BaseService
from .models import User, AuthToken, Friendship, Captcha
from .serializers import UserSerializer, AuthTokenSerializer, CaptchaSerializer
from .serializers import FriendshipSerializer
from datetime import datetime, timedelta
from django.db.models import Q
from customs.services import MessageService
from customs.api_tools import api
import binascii
import os
from django.conf import settings
from customs.delegates import delegate
import itertools


class UserService(BaseService):

    model = User
    serializer = UserSerializer

    @api
    def delete_by_id(self, user_id):
        user = self.get(id=user_id)
        if user:
            user = super(UserService, self).delete(user)
        return user

    def create(self, phone, password, **kwargs):
        kwargs['password'] = password
        kwargs['phone'] = phone
        user = super(UserService, self).create(**kwargs)
        from apps.group.services import GroupService
        GroupService().create_default_home(user.id)
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

    def check_user_is_valid(self, **kwargs):
        user = self.get(**kwargs)

        if user and not user.deleted:
            return True
        else:
            return False

    @api
    def update_by_id(self, user_id, **kwargs):
        new_user = super(UserService, self).update_by_id(user_id, **kwargs)
        return new_user

    @transaction.atomic
    @api
    def lazy_delete_user(self, user):
        user = self.update(user, deleted=True)
        return user

    def check_phone_valid(self, phone):
        PHONE_LENGTH = 11
        return len(phone) == PHONE_LENGTH

    def check_register_info(self, phone, password):
        valid_info = self.check_phone_valid(phone) and self.check_pwd_formatted(password)
        registed_again = self.check_if_registed(phone)
        return valid_info, registed_again

    @api
    def register(self, phone, password, **kwargs):
        user = None

        if not self.check_if_registed(phone):
            user = self.create(phone, password, **kwargs)
            user = authenticate(username=phone, password=password)

        return user

    def check_pwd_formatted(self, password):
        PWD_LENGTH = 6
        return len(password) >= PWD_LENGTH

    def check_if_credential(self, phone, password):
        user = None
        try:
            user = authenticate(username=phone, password=password)
        except AttributeError as e:
            print e
            return False

        if user:
            return True
        else:
            return False

    def check_if_activated(self, phone):
        user = self.get(phone=phone)
        if user:
            return user.activated
        else:
            return False

    @api
    def login_user(self, phone, password):
        if self.check_if_credential(phone, password):
            user = authenticate(username=phone, password=password)
            AuthService().refresh_user_token(user.id)
            return user
        else:
            return None


class AuthService(BaseService):
    model = AuthToken
    serializer = AuthTokenSerializer

    def refresh_user_token(self, user_id):
        token = self.get(user_id=user_id)
        if token:
            token.key = self._generate_key()
            token.created_at = datetime.now()
            token.expired_at = datetime.now() + timedelta(hours=24 * settings.AUTHTOKEN_EXPIRED_DAYS)
            token.save()
            UserService().update_by_id(user_id, token=token)
            return token.key
        else:
            return None

    def get_token(self, user_id):
        token = self.get(user_id=user_id)
        if not token:
            return None
        else:
            return token.key

    def _generate_key(self):
        return binascii.hexlify(os.urandom(16)).decode()

    def check_auth_token(self, user_id, token):
        token_obj = self.get(user_id=user_id)
        valid = False
        if token_obj:
            if token_obj.key == token and not token_obj.expired():
                valid = True
        return valid


class CaptchaService(BaseService):
    model = Captcha
    serializer = CaptchaSerializer

    def _expired(self, captcha_obj):
        VALID_MIN = 10
        valid_time = 60 * VALID_MIN
        # valid time is 10 mins.

        created_time = captcha_obj.created_at
        if (datetime.now() - created_time).seconds > valid_time:
            return True
        return False

    def get_new_captch(self, phone):
        code_length = 6
        return str(int(phone[:code_length]) * datetime.now().microsecond)[0:code_length]

    def get_captcha_code_from_obj(self, captcha_obj):
        captcha_code = captcha_obj.code

        if self._expired(captcha_obj):
            captcha_code = self.get_new_captch(captcha_obj.phone)
            self.update(captcha_obj, code=captcha_code, created_at=datetime.now())

        return captcha_code

    def get_captch(self, phone):
        captcha_obj = self.get(phone=phone)
        captcha_code = None
        if captcha_obj:
            captcha_code = self.get_captcha_code_from_obj(captcha_obj)
        else:
            captcha_code = self.get_new_captch(str(phone))
            self.create(phone=phone, code=captcha_code)

        return captcha_code

    def send_captcha(self, phone, captcha):
        send_succeed = MessageService.send_captcha(phone=phone, captcha=captcha)
        return send_succeed

    def check_captcha(self, phone, captcha):
        captcha_obj = self.get(phone=phone, code=captcha)
        if captcha_obj and not self._expired(captcha_obj):
            return True
        return False


class FriendshipService(BaseService):
    model = Friendship
    serializer = FriendshipSerializer

    def _sort_user(self, user_a_id, user_b_id):
        if user_a_id > user_b_id:
            user_a_id, user_b_id = user_b_id, user_a_id
        return user_a_id, user_b_id

    def create_friendship(self, user_a_id, user_b_id):
        '''
        Creates friendship between user_a and user_b
        '''

        user_a_valid = UserService().check_user_is_valid(id=user_a_id)
        user_b_valid = UserService().check_user_is_valid(id=user_b_id)

        created = True

        if not user_a_valid or not user_b_valid:
            created = False
        elif user_a_id != user_b_id:
            self.create(user_a_id, user_b_id)
            created = True

        return created

    def create(self, user_a_id, user_b_id):
        user_a_id, user_b_id = self._sort_user(user_a_id, user_b_id)
        if str(user_a_id) != str(user_b_id):
            friendship = self.get(user_a_id, user_b_id)
            if not friendship:
                friendship = super(FriendshipService, self).create(user_a=user_a_id, user_b=user_b_id)
            elif friendship.deleted:
                friendship = super(FriendshipService, self).update(friendship, deleted=False)
            return friendship
        else:
            return None
                
    def delete(self, user_a_id, user_b_id):
        '''
        Deletes friendship between user_a and user_b
        '''
        user_a_id, user_b_id = self._sort_user(user_a_id, user_b_id)

        friendship = self.get(user_a_id, user_b_id)

        if friendship:
            friendship = super(FriendshipService, self).delete(friendship)
        return friendship

    def update(self, user_a_id, user_b_id, **kwargs):
        '''
        Update info of two user.
        '''
        user_a_id, user_b_id = self._sort_user(user_a_id, user_b_id)
        friendship = self.get(user_a_id, user_b_id)
        if friendship:
            friendship = super(FriendshipService, self).update(friendship, **kwargs)

        return friendship

    def get(self, user_a_id, user_b_id):
        '''
        Get infor of user_a and user_b
        '''
        user_a_id, user_b_id = self._sort_user(user_a_id, user_b_id)
        return super(FriendshipService, self).get(user_a=user_a_id, user_b=user_b_id)

    def add_friends(self, user_id, friend_ids):
        '''
        Lets friend_ids (may be a list, set or some other collection) all user to
        be the friend of user_id, which is the first arg.

        Returns:

        returns the number of succeed build number.
        '''

        created_result = map(lambda u: self.create_friendship(user_id, u), friend_ids)
        succeed_num = len(filter(lambda created_succeed: created_succeed, created_result))

        return succeed_num

    def is_friend(self, user_a_id, user_b_id):
        '''
        Gets if is frend between user_a and user_b
        '''

        test_self = user_a_id == user_b_id

        result = False

        if not test_self:
            friendship = self.get(user_a_id, user_b_id)
            if friendship and not friendship.deleted:
                result = True
            else:
                result = False
        else:
            result = True

        return result

    def all_is_friend(self, user_ids):
        '''
        Judges if the user of user_ids all is friend each other.
        '''

        all_is = None

        for u1, u2 in itertools.product(user_ids, user_ids):
            if not self.is_friend(u1, u2):
                all_is = False
                break
        else:
            all_is = True

        return all_is

    def get_user_friend_ids(self, user_id):
        condition = Q(user_a=user_id) | Q(user_b=user_id)
        friends = super(FriendshipService, self).get(condition, many=True)

        def get_user_friend(user_id, f):
            '''
            f.user_a and f.user_b could be user_id or user_id's friend_ids
            so remove user_id from id pair and pop(), will get it's firend id
            '''
            pair = [f.user_a, f.user_b]
            pair.remove(user_id)
            return pair.pop()

        ids = map(lambda f: get_user_friend(user_id, f), friends)

        return ids

user_service = delegate(UserService(), serialize_func=UserService().serialize)
captcha_service = delegate(CaptchaService(), serialize_func=CaptchaService().serialize)
auth_service = delegate(AuthService(), serialize_func=AuthService().serialize)
friend_service = delegate(FriendshipService(), serialize_func=FriendshipService().serialize)
