# -*- coding:utf-8 -*-

# from django.db import transaction

from customs.services import BaseService
from .models import Image
from .serializers import ImageSerializer


class ImageService(BaseService):

    @classmethod
    def _get_model(cls, name='Image'):
        if name == 'Image':
            return Image

    @classmethod
    def get_serializer(cls, model='Image'):
        if model == 'Image':
            return ImageSerializer

    @classmethod
    def serialize(cls, obj, context={}):
        if isinstance(obj, Image):
            return ImageSerializer(obj, context=context).data

    @classmethod
    def get_image(cls, **kwargs):
        return Image.objects.get_or_none(**kwargs)

    @classmethod
    def get_images(cls, **kwargs):
        return Image.objects.filter(**kwargs)
