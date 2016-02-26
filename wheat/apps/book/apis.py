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
        '''
        获得关于作者的信息，根据参数的不同可以获得单个user的和user_group的信息

        ### Request Example:

        /author/type=person&id=asdhjk21hjkads2134

        获取用户id为XXX的个人信息

        /author/type=group&id=asdhjk21hjkads2134

        获取作者群组id为XXX的群组信息

        type -- 查询类型 (person | group)
        id -- 用户或者group的id (String)

        ---

        '''
        pass

    def create(self, request):
        '''
        根据user_id列表生成一个“作者群”

        '''
        pass


class BookViewSet(ListModelMixin, viewsets.GenericViewSet):
    model = BookService.get_model()
    queryset = model.get_queryset()
    serializer_class = BookService.get_serializer()
    lookup_field = 'id'
    permission_classes = [
    Or(permissions.IsAuthenticatedOrReadOnly, AllowPostPermission,)]

    def list(self, request):
        '''
        获得关于书本的信息
        ---
        id -- Book id
        '''
        pass

    def create(self, request):
        '''
        创建书籍信息
        '''
        pass

    def update(self, request, book_id):
        '''
        更新书籍信息
        '''
        pass


class OrderViewSet(ListModelMixin, viewsets.GenericViewSet):
    model = OrderService.get_model()
    queryset = model.get_queryset()
    serializer_class = OrderService.get_serializer()
    lookup_field = 'id'
    permission_classes = [
    Or(permissions.IsAuthenticatedOrReadOnly, AllowPostPermission,)]
    
    def list(self, reqeust):
        '''
        '''
        pass

    def create(self, request):
        '''
        '''
        pass

    def update(self, request, order_id):
        '''
        '''
        pass
