# -*- coding:utf-8 -*-

from rest_framework import viewsets, status
from django.core.files.uploadedfile import InMemoryUploadedFile

from customs.response import SimpleResponse
from .services import ImageService
import datetime
import threading
from customs import class_tools

    
@class_tools.default_view_set
class ImageViewSet(viewsets.GenericViewSet):
    def create(self, request):
        """
        Upload an image.
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: image
              type: file
        """
        IMAGE = 'image'
        start_time = datetime.datetime.now()
        if IMAGE not in request.data or not isinstance(request.data[IMAGE], InMemoryUploadedFile):
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST)
        request.data[IMAGE].name = \
            str(datetime.datetime.now().microsecond) \
            + str(request.data[IMAGE].name)

        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            t = threading.Thread(target=ImageService.save_image_by_ratio, args=[request.data[IMAGE]])
            t.setDaemon(False)
            t.start()
            serializer.save()
            end_time = datetime.datetime.now()
            print(end_time - start_time)
            return SimpleResponse(serializer.data, status=status.HTTP_201_CREATED)
        return SimpleResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        """
        List all images.
        ---
        omit_serializer: true
        """
        images = ImageService.get_images()
        data = ImageService.serialize_objs(images)
        return SimpleResponse(data)
