# -*- coding:utf-8 -*-

from django.db import models
import uuid
from uuidfield import UUIDField
from imagekit.models import ProcessedImageField
from imagekit.processors import Transpose

from customs.models import EnhancedModel, CacheableManager, CommonUpdateAble


class Image(CommonUpdateAble, models.Model, EnhancedModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = ProcessedImageField(
        upload_to='origin',
        height_field='height',
        width_field='width',
        processors=[Transpose()],  # ResizeToFit(640)
        options={'quality': 100})
    image_url = models.URLField(max_length=300, blank=True)
    # description = models.CharField(max_length=200, blank=True)
    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)
    orientation = models.PositiveIntegerField(default=1)
    deleted = models.BooleanField(default=False)

    objects = CacheableManager()

    class Meta:
        db_table = 'image'
