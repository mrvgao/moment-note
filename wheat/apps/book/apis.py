# -*- coding:utf-8 -*-

from rest_framework import permissions, viewsets, status
from rest_condition import Or

from customs.permissions import AllowPostPermission
from customs.response import SimpleResponse
from customs.viewsets import ListModelMixin
from apps.user.permissions import admin_required, login_required
from .services import AuthorService, BookService, OrderService
from errors import codes


class AuthorViewSet(ListModelMixin, viewsets.GenericViewSet):
    model = AuthorService.get_model()
    queryset = model.get_queryset()
    serializer_class = AuthorService.get_serializer()
    lookup_field = 'id'
    permission_classes = [
    Or(permissions.IsAuthenticatedOrReadOnly, AllowPostPermission,)]

    def list(self, request):
        pass

    def create(self, request):
        pass


class BookViewSet(ListModelMixin, viewsets.GenericViewSet):
    model = BookService.get_model()
    queryset = model.get_queryset()
    serializer_class = BookService.get_serializer()
    lookup_field = 'id'
    permission_classes = [
    Or(permissions.IsAuthenticatedOrReadOnly, AllowPostPermission,)]

    def list(self, request):
        pass

    def create(self, request):
        pass

    def update(self, request, book_id):
        pass


class OrderViewSet(ListModelMixin, viewsets.GenericViewSet):
    model = OrderService.get_model()
    queryset = model.get_queryset()
    serializer_class = OrderService.get_serializer()
    lookup_field = 'id'
    permission_classes = [
    Or(permissions.IsAuthenticatedOrReadOnly, AllowPostPermission,)]
    
    def list(self, reqeust):
        pass

    def create(self, request):
        pass

    def update(self, request, order_id):
        pass
