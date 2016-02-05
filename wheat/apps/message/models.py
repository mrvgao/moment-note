# -*- coding:utf-8 -*-

import uuid
from django.db import models
from uuidfield import UUIDField
from jsonfield import JSONField

from customs.models import EnhancedModel, CommonUpdateAble, CacheableManager


class Message(CommonUpdateAble, models.Model, EnhancedModel):
    CONTENT_TYPES = (
        ('text', u'文字'),
        ('pic', u'图片'),
        ('emoji', u'表情'),
        ('link', u'链接'),
        ('voice', u'语音'),
        ('video', u'视频'),
        ('song', u'歌曲'),
        ('location', u'位置'),
    )
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender_id = UUIDField(db_index=True)
    receiver_id = UUIDField(db_index=True)
    content_type = models.CharField(max_length=15, choices=CONTENT_TYPES)
    content = JSONField(default={})
    post_date = models.DateTimeField(auto_now_add=True, db_index=True)
    received = models.BooleanField(default=False, db_index=True)

    objects = CacheableManager()

    class Meta:
        db_table = 'message'

    @classmethod
    def valid_content_type(cls, content_type):
        for t, d in Message.CONTENT_TYPES:
            if t == content_type:
                return True
        return False

    @classmethod
    def valid_content(cls, content):
        if not isinstance(content, dict):
            return False
        return True


class GroupMessage(CommonUpdateAble, models.Model, EnhancedModel):
    CONTENT_TYPES = (
        ('text', u'文字'),
        ('pic', u'图片'),
        ('emoji', u'表情'),
        ('link', u'链接'),
        ('voice', u'语音'),
        ('video', u'视频'),
        ('song', u'歌曲'),
        ('location', u'位置'),
    )
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender_id = UUIDField(db_index=True)
    group_id = UUIDField(db_index=True)
    receiver_id = UUIDField(db_index=True)
    content_type = models.CharField(max_length=15, choices=CONTENT_TYPES)
    content = JSONField(default={})
    post_date = models.DateTimeField(auto_now_add=True, db_index=True)
    received = models.BooleanField(default=False, db_index=True)

    objects = CacheableManager()

    class Meta:
        db_table = 'group_message'

    @classmethod
    def valid_content_type(cls, content_type):
        for t, d in Message.CONTENT_TYPES:
            if t == content_type:
                return True
        return False

    @classmethod
    def valid_content(cls, content):
        if not isinstance(content, dict):
            return False
        return True
