# -*- coding:utf-8 -*-

import uuid
from uuidfield import UUIDField
from django.db import models
from jsonfield import JSONCharField, JSONField

from customs.models import EnhancedModel, CommonUpdateAble, CacheableManager


class MultiAuthorGroup(CommonUpdateAble, models.Model, EnhancedModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator_id = UUIDField(db_index=True)  # 创建者
    members = JSONField(default={})  # 成员列表
    max_members = models.SmallIntegerField(default=15)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CacheableManager()

    class Meta:
        db_table = "muti_author_group"


class Book(CommonUpdateAble, models.Model, EnhancedModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator_id = UUIDField(db_index=True)
    group_id = UUIDField(db_index=True)
    remark_name = models.CharField(max_length=50)  # The remark name of this book.
    avatar = models.CharField(max_length=100)  # The book avatar.
    book_name = models.CharField(max_length=50)
    author = models.CharField(max_length=50)  # wroten name
    page_format = models.CharField(max_length=50)
    preview_url = models.CharField(max_length=50)
    creator_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    objects = CacheableManager()

    class Meta:
        db_table = "book"


class Order(CommonUpdateAble, models.Model, EnhancedModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_id = UUIDField(db_index=True)  # 创建者
    price = models.FloatField()
    status = models.CharField(max_length=512)
    creator_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now_add=True)
    info = JSONCharField(max_length=512, default={})

    objects = CacheableManager()

    class Meta:
        db_table = 'order'