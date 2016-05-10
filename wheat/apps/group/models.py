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
        ('all_home_member', u'所有好友'),
    )
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_type = models.CharField(
        max_length=15,
        choices=GROUP_TYPES,
        db_index=True
    )
    name = models.CharField(max_length=50)
    avatar = ProcessedImageField(
        max_length=100,
        upload_to='avatars',
        processors=[Transpose(), ResizeToFit(150)],
        format='JPEG',
        options={'quality': 85})
    creator_id = UUIDField(db_index=True)  # 创建者
    admins = JSONCharField(max_length=512, default={})  # 管理员
    members = JSONField(default={})  # 成员列表
    max_members = models.SmallIntegerField(default=15)
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

    @classmethod
    def get_home_member(cls, user_id):
        members = []

        group = cls.objects.get_or_none(
            creator_id=user_id,
            group_type='all_home_member'
        )

        if group:
            for m in group.members:
                members.append(m)
            return members
        else:
            return [user_id]

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
    role = models.CharField(max_length=15)
    nickname = models.CharField(max_length=30)  # 个人在群里的名称
    avatar = models.CharField(max_length=100)  # 个人在群里的头像
    joined_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    objects = CacheableManager()

    class Meta:
        db_table = "group_member"


class Invitation(CommonUpdateAble, models.Model, EnhancedModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inviter = UUIDField(db_index=True)  # 邀请者
    invitee = models.CharField(max_length=100, db_index=True)  # 被邀请者，可能是id,phone,email
    group_id = UUIDField()  # 被邀请到哪个group
    role = models.CharField(max_length=15)  # 被邀请的角色
    message = JSONCharField(max_length=512, default={})  # 邀请的信息
    invite_time = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    accept_time = models.DateTimeField(null=True, blank=True, default=None)
    deleted = models.BooleanField(default=False)  # 明确不接受则deleted=True
    notified = models.BooleanField(default=False)  # 是否通知inviter接受或者不接受

    objects = CacheableManager()

    class Meta:
        db_table = 'invitation'
