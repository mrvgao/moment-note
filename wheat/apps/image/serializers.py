# -*- coding:utf-8 -*-

from rest_framework import serializers

from customs.serializers import XModelSerializer
from .models import Image


class ImageSerializer(XModelSerializer):
    image = serializers.ImageField(
        required=False, max_length=100, allow_empty_file=False, use_url=True, style={'input_type': 'file'})
    image_url = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = Image
        fields = ('id', 'image', 'image_url',
                  'height', 'width', 'orientation', 'deleted')
