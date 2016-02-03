# -*- coding:utf-8 -*-

import uuid
from uuidfield import UUIDField
from django.db import models
from jsonfield import JSONCharField, JSONField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit, Transpose

from customs.models import EnhancedModel, CommonUpdateAble, CacheableManager


class Group(CommonUpdateAble, models.Model, EnhancedModel):
    GROUP_TYPES = (
        ('common', u'普通群'),
        ('family', u'家庭'),
    )
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_type = models.CharField(max_length=15, choices=GROUP_TYPES, db_index=True)
    name = models.CharField(max_length=50)
    avatar = ProcessedImageField(max_length=100,
                                 upload_to='avatars',
                                 processors=[Transpose(), ResizeToFit(150)],
                                 format='JPEG',
                                 options={'quality': 85})
    creator_id = UUIDField(db_index=True)  # 创建者
    admins = JSONCharField(max_length=512, default={})  # 管理员
    members = JSONField(default={})  # 成员列表
    settings = JSONCharField(max_length=512, default={})  # 更多的一些设置
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CacheableManager()

    class Meta:
        db_table = "group"

    @classmethod
    def valid_group_type(cls, group_type):
        for t, d in Group.GROUP_TYPES:
            if t == group_type:
                return True
        return False


# class GroupProfile(models.Model):
#     ''' 更多的关于群的信息，包括一些个性化的东西，比如皮肤啊 '''
#     group_id = UUIDField(primary_key=True)
#     country = models.CharField(max_length=30, blank=True)
#     province = models.CharField(max_length=30, blank=True)
#     city = models.CharField(max_length=30, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = "group_profile"


class GroupMember(CommonUpdateAble, models.Model, EnhancedModel):
    AUTHORITIES = (
        ("common", u"普通成员"),
        ("admin", u"管理员"),
    )
    member_id = UUIDField(db_index=True)
    group_id = UUIDField(db_index=True)
    authority = models.CharField(max_length=10, choices=AUTHORITIES, default="common")
    group_remark_name = models.CharField(max_length=50)  # 个人对群的备注名称
    nickname = models.CharField(max_length=40)  # 个人在群里的名称
    avatar = models.CharField(max_length=100)  # 个人在群里的头像
    send_msg_count = models.IntegerField(default=0)  # 个人的消息计数
    receive_msg_count = models.IntegerField(default=0)  # 其他人的消息计数
    unread_msgs = models.IntegerField(default=0)  # 有几条未读的消息
    joined_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    objects = CacheableManager()

    class Meta:
        db_table = "group_member"
