# -*- coding:utf-8 -*-

import uuid
import binascii
import os
import time
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.conf import settings
from django.dispatch import receiver
from datetime import datetime, timedelta
from uuidfield import UUIDField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit, Transpose
from django.db.models.signals import post_save

from customs.models import EnhancedModel, CommonUpdateAble, CacheableManager
from .managers import UserManager, AuthTokenManager


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created and instance is not None:
        AuthToken.objects.create(user_id=instance.id)


class AuthToken(EnhancedModel, CommonUpdateAble, models.Model):

    """
    The default authorization token model.
    """
    key = models.CharField(max_length=32)
    user_id = models.CharField(max_length=32, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

    objects = AuthTokenManager()

    class Meta:
        db_table = 'auth_token'

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self._generate_key()

        if not self.expired_at:
            self.expired_at = datetime.now() + timedelta(hours=24 * settings.AUTHTOKEN_EXPIRED_DAYS)
        return super(AuthToken, self).save(*args, **kwargs)

    def _generate_key(self):
        return binascii.hexlify(os.urandom(16)).decode()

    @property
    def expired_timestamp(self):
        return int(time.mktime(self.expired_at.timetuple()))

    def expired(self):
        return self.expired_at < datetime.now()

    @property
    def user(self):
        if hasattr(self, '_user'):
            return self._user
        else:
            self._user = User.objects.get_or_none(id=self.user_id)
            return self._user

    @property
    def token(self):
        return {
            'token': self.key,
            'expired_at': self.expired_timestamp,
            'expired': self.expired()
        }

    def __str__(self):
        return self.key


class User(AbstractBaseUser, EnhancedModel, CommonUpdateAble):
    GENDERS = (
        ('M', u'男'),
        ('F', u'女'),
        ('N', u'未知'),
    )
    ROLES = (
        ('normal', u'普通用户'),
        ('tutor', u'麦粒导师'),
    )

    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=18, unique=True)  # 必填项，且唯一
    nickname = models.CharField(max_length=30)  # 昵称如果不填默认就是张小姐、陈先生
    first_name = models.CharField(max_length=20, blank=True)  # 名字选填
    last_name = models.CharField(max_length=20)  # 姓氏必填
    full_name = models.CharField(max_length=40, blank=True, db_index=True)  # 可起到搜索作用
    avatar = ProcessedImageField(
        max_length=100,
        upload_to='avatars',
        processors=[Transpose(), ResizeToFit(150)],
        format='JPEG',
        options={'quality': 85})
    tagline = models.CharField(max_length=100, blank=True)  # 个人的签名档
    gender = models.CharField(max_length=1, default='N', choices=GENDERS)
    marital_status = models.CharField(max_length=1, default='U', null=True)  # 婚否
    birthday = models.DateField(null=True, blank=True, default=None)
    country = models.CharField(max_length=30, blank=True)
    province = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=10, choices=ROLES, default="normal")
    is_admin = models.BooleanField(default=False)
    activated = models.BooleanField(default=True)  # 默认激活
    activated_at = models.DateTimeField(auto_now_add=True)  # 激活的时间
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone'
    # REQUIRED_FIELDS = ['phone']

    objects = UserManager()

    class Meta:
        db_table = 'user'

    @property
    def is_superuser(self):
        return self.is_admin

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def token(self):
        tk = AuthToken.objects.get(user_id=self.id)
        return tk.token

    @property
    def token_expired(self):
        return self.token['expired']


class Relationship(CommonUpdateAble, models.Model, EnhancedModel):
    ''' 血缘关系表 '''
    RELATIONS = (
        ('husband-wife', u'夫妻'),
        ('father-child', u'父子/女'),
        ('mother-child', u'母子/女'),
    )
    from_user_id = UUIDField(db_index=True)
    to_user_id = UUIDField(db_index=True)
    relation = models.CharField(max_length=15, db_index=True,
                                choices=RELATIONS)  # 关系的名称
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "relationship"


class Friendship(CommonUpdateAble, models.Model, EnhancedModel):
    ''' 好友关系表，包含了血缘关系 '''
    user_a = UUIDField(db_index=True)
    user_b = UUIDField(db_index=True)
    inviter = UUIDField(null=True, blank=True, default='')  # 关系的发起者
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "friendship"
        unique_together = ('user_a', 'user_b')


class UserCounter(CommonUpdateAble, models.Model, EnhancedModel):
    ''' 计数器: 用在一些需要计数的地方，比如多少条未读消息，多少条新状态 '''
    user_id = UUIDField(primary_key=True)
    unread_msgs = models.IntegerField(default=0)
    unread_feeds = models.IntegerField(default=0)
    unread_comments = models.IntegerField(default=0)
    unread_invitations = models.IntegerField(default=0)
    unread_topics = models.IntegerField(default=0)
    chat_ats = models.IntegerField(default=0)
    feed_ats = models.IntegerField(default=0)
    # should be more...
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_counter'


class Captcha(CommonUpdateAble, models.Model, EnhancedModel):
    ''' 验证码：分不同purposes，可能是发到手机，也可能是发到邮箱 '''
    PURPOSES = (
        ('register', u'注册用户'),
        ('changeEmail', u'更换邮箱'),
        ('resetPasswd', u'重置密码')
    )
    phone = models.CharField(max_length=18)
    code = models.CharField(max_length=10, db_index=True)  # 验证码
    purpose = models.CharField(max_length=15, choices=PURPOSES, default='register')
    created_at = models.DateTimeField(auto_now_add=True)
    send_at = models.DateTimeField(blank=True, null=True, default=None)
    send = models.BooleanField(default=False)
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(blank=True, null=True, default=None)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'captcha'


class AppSetting(CommonUpdateAble, models.Model, EnhancedModel):
    ''' App的一些设置 '''
    user_id = UUIDField(primary_key=True)
    language = models.CharField(max_length=10)
    background_pic = models.CharField(max_length=50)
    searchable = models.BooleanField(default=True)
    remind_of_new_msg = models.BooleanField(default=True)
    auto_update = models.BooleanField(default=True)
    # should be more...

    class Meta:
        db_table = 'app_setting'
