# -*- coding:utf-8 -*-

from rest_framework import permissions, viewsets, status
from rest_condition import Or

from customs.permissions import AllowPostPermission
from customs.response import SimpleResponse
from customs.viewsets import ListModelMixin
from apps.user.permissions import admin_required, login_required
from .services import AuthorService, BookService, OrderService
from apps.user.services import UserService
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
        id -- 用户或者group的id (String), !注意， id两个字母均为小写
        ---
        omit_serializer: true

        '''
        TYPE, ID = 'type', 'id'
        PERSON, GROUP = 'person', 'group'
        query_type = request.query_params.get(TYPE, None)
        query_id = request.query_params.get(ID, None)

        if query_type == GROUP:
            data = AuthorService.get_author_group(group_id=query_id)
            return SimpleResponse(data)
        elif query_type == PERSON:
            user = UserService.get_user(id=query_id)
            data = UserService.serialize(user)
            return SimpleResponse(data)
        else:
            return SimpleResponse(success=False, errors="Params Unvlid")

    @login_required
    def create(self, request):
        '''
        根据user_id列表生成一个“作者群”
        使用场景：选择若干用户 然后形成一个用户群 进行图书编辑

        ### Example Request:

            {
                "user_id":[user_id_1, user_id_2],
                "creator_id": user_id
            }

        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body

        '''

        USER_ID, CREATOR_ID = 'user_id', 'creator_id'
        user_id_list = request.data.get(USER_ID)
        creator_id = request.data.get(CREATOR_ID)

        if user_id_list and creator_id:
            author_group = AuthorService.create_author_group(
                creator_id, user_id_list)
            data = AuthorService.serialize(author_group)
            return SimpleResponse(data)
        else:
            return SimpleResponse(
                success=False, erros="Params Unvalid"
            )


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

        id -- Book id
        ---
        omit_serializer: true
        '''
        pass

    @login_required
    def create(self, request):
        '''
        创建书籍信息
        使用场景： 新书后台点击制作书本完成之后，后台即创建一本书

        创建一本书所需要的信息：
        creator_id: 这本书的创建者的id
        avatar: 这本书的封面图的URL
        book_name: 为该书所起的名字
        author: 该书的作者的名字（若无则与用户的昵称相同）
        page_format: 该书的板式
        preview_url: 该书预览页的URL

        ### Request Example

            {
                "creator_id": String, (required)
                "group_id": String, (所隶属的作者组， required)
                "avatar": String,
                "book_name": String,
                "author": String,
                "page_format": String,
                "preview_url": String
            }

        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body
        '''

        CREATOR_ID = 'creator_id'

        creator_id = request.data.get(CREATOR_ID, None)
        if str(creator_id) != str(request.user.id):
            return SimpleResponse(success=False, errors="Not Login")
        else:
            try:
                book = BookService.create_book(**request.data)
                data = BookViewSet.serializer_class(book).data
                return SimpleResponse(data)
            except KeyError:
                return SimpleResponse(success=False, errors="Lacks of args")

    def update(self, request, book_id):
        '''
        更新书籍信息
        使用场景： 新书后台制作书本完成之后，将书籍相关的信息，使用put方式发送过来，更改其中的预览路径、封面图URL等信息
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
