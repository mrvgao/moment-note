# -*- coding:utf-8 -*-

from rest_framework import permissions, viewsets, status
from rest_condition import Or

from customs.permissions import AllowPostPermission
from customs.response import SimpleResponse
from customs.viewsets import ListModelMixin
from apps.user.permissions import admin_required, login_required
from .services import AuthorService, BookService, OrderService
from .services import update_book_field
from apps.user.services import UserService
import services
from errors import codes
from .utility import login_wxbook
from .services import send_create_book_request_to_wxbook
from .services import delete_book_list_some_field
from utils.redis_utils import publish_redis_message
from rest_framework.decorators import list_route
from customs import class_tools


@class_tools.default_view_set
class AuthorViewSet(ListModelMixin, viewsets.GenericViewSet):
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
            data = AuthorService.get_author_group_info(
                group_id=query_id, user_service=UserService
            )

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
                success=False, errors="Params Unvalid"
            )


class BookViewSet(ListModelMixin, viewsets.GenericViewSet):
    model = BookService.get_model()
    queryset = model.get_queryset()
    serializer_class = BookService.get_serializer()
    lookup_field = 'id'
    permission_classes = [
        Or(permissions.IsAuthenticatedOrReadOnly, AllowPostPermission,)]

    @login_required
    def list(self, request):
        '''
        获得书本的列表

        creator_id -- creator's id
        ---
        omit_serializer: true
        '''
        CREATOR_ID = 'creator_id'
        _CREATOR_ID = request.query_params.get(CREATOR_ID, None)
        # TODO: page
        if _CREATOR_ID:
            books = BookService.get_books(creator_id=_CREATOR_ID, deleted=False)
        else:
            books = BookService.get_books(deleted=False)
        return SimpleResponse(BookService.serialize_objs(books))

        # books = super(BookViewSet, self).list(request)
        # book_data = books.data
        # if _CREATOR_ID:
        #     book_data = filter(
        #         lambda b: b[CREATOR_ID] == _CREATOR_ID, book_data
        #     )

        #     DELETED = 'deleted'
        #     book_data = filter(
        #         lambda b: b[DELETED] is False, book_data
        #     )

        #     book_data = delete_book_list_some_field(book_data)

        # return SimpleResponse(book_data)
#        CREATOR = 'creator'
#        creator_id = request.query_params.get(CREATOR, None)
#        if book:
#            book_data = BookViewSet.serializer_class(book).data
#            return SimpleResponse(book_data)
#        else:
#            return SimpleResponse(
#                success=False, code=404, errors='this book not exist'
#            )

    @login_required
    def destroy(self, request, id):
        '''
        Delete One Book By Book's id
        ---
        omit_serializer: true
        '''
        BOOK_ID = id

        try:
            deleted = BookService.delete_book(request.user.id, BOOK_ID)
            data = {'datelated': deleted, 'book_id': BOOK_ID}
            return SimpleResponse(data=data)
        except ReferenceError as e:
            return SimpleResponse(success=False, errors=e.message)

    @login_required
    @login_wxbook
    def create(self, request):
        '''
        创建书籍信息
        使用场景： 新书后台点击制作书本完成之后，后台即创建一本书

        创建一本书所需要的信息：
        creator_id: 这本书的创建者的id
        cover: 这本书的封面图的URL
        book_name: 为该书所起的名字
        author: 该书的作者的名字（若无则与用户的昵称相同）
        page_format: 该书的板式
        preview_url: 该书预览页的URL

        ### Request Example

            {
                "creator_id": String, (required)
                "group_id": String, (所隶属的作者组， required)
                "cover": String,
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
                book_id = book.id
                group_id = book.group_id
                send_create_book_request_to_wxbook(
                    book_id=book_id, group_id=group_id, creator_id=creator_id)
                data = BookViewSet.serializer_class(book).data
                return SimpleResponse(data)
            except KeyError:
                return SimpleResponse(success=False, errors="Lacks of args")
            except ReferenceError:
                return SimpleResponse(success=False, errors="Cannot connect to wx book")

    @login_required
    def retrieve(self, request, id):
        '''
        Retrieve Book info.
        ---
        omit_serializer: true
        '''
        book = BookService.get_book(id=id)
        if not book:
            return SimpleResponse(status=status.HTTP_404_NOT_FOUND)
        return SimpleResponse(BookViewSet.serializer_class(book).data)

    def update(self, request, id):
        '''
        根据author_group_id更新书籍信息
        使用场景： 新书后台制作书本完成之后，将书籍相关的信息，使用put方式发送过来，更改其中的预览路径、封面图URL等信息

        ### Example Request:
            {
                "cover": json String,
                "book_name": String,
                "author": String,
                "page_format": String,
                "preview_url": String,
                "page_num": int,
                "from_date": "2015-03-01 00:00:00",
                "to_date": "2016-03-01 00:00:00"
            }
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body

        '''

        book = BookService.get_book(id=id)
        if book:
            new_book = services.update_book_field(book, request.data)
            new_book = BookService.get_book(id=id)  # hot fix
            new_book_data = BookViewSet.serializer_class(new_book).data
            msg = {
                'book_id': new_book.id,
                'receiver_id': new_book.creator_id,
                'event': 'book',
                'book': new_book_data
            }
            publish_redis_message('book', msg)
            return SimpleResponse(new_book_data)
        else:
            return SimpleResponse(success=False, errors='this book not exist')


class OrderViewSet(ListModelMixin, viewsets.GenericViewSet):
    model = OrderService.get_model()
    queryset = model.get_queryset()
    serializer_class = OrderService.get_serializer()
    lookup_field = 'id'
    permission_classes = [
        Or(permissions.IsAuthenticatedOrReadOnly, AllowPostPermission,)]

    def list(self, request):
        '''
        Get order information by order id

        id -- order's id
        ---
        omit_serializer: true
        omit_parameters:
            - form
        '''
        ID = 'id'
        order_id = request.query_params.get(ID, None)
        order = OrderService.get_order(id=order_id)
        if order:
            order_data = OrderViewSet.serializer_class(order).data
            return SimpleResponse(order_data)
        else:
            return SimpleResponse(success=False, errors='this order not exist')

    def create(self, request):
        '''
        Create Order Information

        ### Example Request:

            {
                "book_id": String, (required)
                "price": Float,
                "status": String,
                "info": String,
            }
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body
        '''

        try:
            order = OrderService.create_order(**request.data)
            data = OrderViewSet.serializer_class(order).data
            return SimpleResponse(data)
        except KeyError:
            return SimpleResponse(success=False, errors="Lack of requied keys")

    def update(self, request, id):
        '''
        根据书本的id，更新订单信息
        Update Order Information.

        ### Example Request:

            {
                "price": Float,
                "status": String,
                "info": JSON
            }

        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body
        '''

        order = OrderService.get_order(book_id=id)
        if order:
            new_order = services.update_order_field(order, request.data)
            new_order_data = OrderViewSet.serializer_class(new_order).data
            return SimpleResponse(new_order_data)
        else:
            return SimpleResponse(success=False, errors='this order not exist')
