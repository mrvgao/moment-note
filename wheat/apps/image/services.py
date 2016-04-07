# -*- coding:utf-8 -*-

# from django.db import transaction

from customs.services import BaseService
from .models import Image
from .serializers import ImageSerializer
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import PIL


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


    @staticmethod
    def save_image_by_ratio(image, ratio=1.0):
        SMALLE_DIR = 'small/'
        LARGE_DIR = 'large/'
        MIDDLE_DIR = 'medium/'
        TEMP = 'temp/'

        SMALL_BASE_WIDTH = 100
        MIDDLE_BASE_WIDTH = 300
        LARGE_BASE_WIDTH = 600

        DIRS = [SMALLE_DIR, MIDDLE_DIR, LARGE_DIR]
        WIDTHS = [SMALL_BASE_WIDTH, MIDDLE_BASE_WIDTH, LARGE_BASE_WIDTH]

        image_origin_data = ContentFile(image.read())

        original_file_name = image.name
        path = default_storage.save(TEMP + original_file_name, image_origin_data)

        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        image = PIL.Image.open(tmp_file)

        for new_dir, new_width in zip(DIRS, WIDTHS):
            small_image_route = os.path.join(
                settings.MEDIA_ROOT,
                new_dir + original_file_name
            )

            ImageService.change_image_base_on_width(
                image=image,
                _WIDTH=new_width,
                _NEW_ROUTE=small_image_route
            )

        os.remove(tmp_file)

    @staticmethod
    def change_image_base_on_width(image, _WIDTH, _NEW_ROUTE):
        wpercent = (_WIDTH/float(image.size[0]))
        hsize = int((float(image.size[1])*float(wpercent)))
        new_image = image.resize((_WIDTH, hsize), PIL.Image.ANTIALIAS)

        directory = os.path.dirname(_NEW_ROUTE)

        if not os.path.exists(directory):
            os.makedirs(directory)

        new_image.save(_NEW_ROUTE)