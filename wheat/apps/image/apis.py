# -*- coding:utf-8 -*-

from rest_framework import permissions, viewsets, status
from rest_condition import Or
from django.core.files.uploadedfile import InMemoryUploadedFile

from customs.permissions import AllowPostPermission
from customs.response import SimpleResponse
from .services import ImageService


class ImageViewSet(viewsets.GenericViewSet):

    model = ImageService._get_model()
    queryset = model.get_queryset()
    serializer_class = ImageService.get_serializer()
    lookup_field = 'id'
    permission_classes = [
        Or(permissions.IsAuthenticatedOrReadOnly, AllowPostPermission,)]

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
        if 'image' not in request.data or not isinstance(request.data['image'], InMemoryUploadedFile):
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
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
