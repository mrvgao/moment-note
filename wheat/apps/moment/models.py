# -*- coding:utf-8 -*-

import uuid
from django.db import models
from uuidfield import UUIDField
from jsonfield import JSONField

from customs.models import EnhancedModel, CommonUpdateAble, CacheableManager
from datetime import datetime


class Moment(CommonUpdateAble, models.Model, EnhancedModel):
    TYPES = (
        ('text', u'文字'),
        ('pics', u'图片'),
        ('pics-text', u'图文'),
        ('link', u'链接'),
        ('voice', u'语音'),
        ('video', u'视频'),
        ('song', u'歌曲'),
        ('location', u'位置'),
    )
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = UUIDField(db_index=True)
    content_type = models.CharField(max_length=10, choices=TYPES)
    content = JSONField(default={})  # {"text": "xx", "pics": []}
    post_date = models.DateTimeField(auto_now_add=True, db_index=True)
    moment_date = models.DateTimeField(auto_now_add=True, db_index=True)
    visible = models.CharField(max_length=32, db_index=True, default='private')  # private, public, friends, group_id
    deleted = models.BooleanField(default=False)

    objects = CacheableManager()

    class Meta:
        db_table = "moment"

    @classmethod
    def valid_content_type(cls, content_type, content):
        TEXT, PICS = 'text', 'pics'
        if not isinstance(content, dict):
            return False
        if content_type == TEXT:
            return TEXT in content.keys() 
        elif content_type == PICS:
            return PICS in content.keys() and isinstance(content['pics'], list)
        elif content_type == 'pics-text':
            return TEXT in content.keys() and PICS in content.keys() and isinstance(content['pics'], list)
        return False

    @classmethod
    def valid_visible_field(cls, visible):
        PRIVATE, PUBLIC, FRIENDS = 'private', 'public', 'friends'
        AVALIABLE_SCOPES = [PRIVATE, PUBLIC, FRIENDS]
        return visible in AVALIABLE_SCOPES or len(visible) == 32


class Comment(CommonUpdateAble, models.Model, EnhancedModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    moment_id = UUIDField(default=None)
    specific_person = UUIDField(null=True)
    sender_id = UUIDField(default=None)
    content = models.CharField(max_length=140, default=None)
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
    deleted = models.BooleanField(default=False, blank=True)


class Mark(CommonUpdateAble, models.Model, EnhancedModel):
    TYPES = (
        ('like', 'like'),
    )

    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    moment_id = UUIDField(default=None)
    sender_id = UUIDField(default=None)
    mark_type = models.CharField(max_length=10, choices=TYPES, default=None)
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
    deleted = models.BooleanField(default=False, blank=True)

    # override save()
    def save(self, *arg, **kwargs):
        if len(Mark.objects.filter(moment_id=self.moment_id)
                .filter(sender_id=self.sender_id)
                .filter(mark_type=self.mark_type)
                .filter(deleted=False)) > 0 and not self.deleted:
            # if have a mark have the same sender and the same moment,
            # and this mark not delelte, and this new mark is not a delete
            # mark, so dont save this new mark.
            print('mark existed')
            return False
        else:
            super(Mark, self).save(*arg, **kwargs)
            return True


class MomentStat(CommonUpdateAble, models.Model, EnhancedModel):
    moment_id = UUIDField(primary_key=True)
    likes = JSONField(default=[])
    shares = JSONField(default=[])
    like_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)

    objects = CacheableManager()

    class Meta:
        db_table = "moment_stat"
