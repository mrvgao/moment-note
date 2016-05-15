# -*- coding:utf-8 -*-

from datetime import datetime
from django.db import transaction

from customs.services import BaseService
from apps.user.services import UserService
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer
import ast
from functools import partial
from customs import funcs
import requests


class AuthorService:

    @staticmethod
    def get_serializer():
        return AuthorSerializer

    @staticmethod
    def get_model():
        return Author

    @staticmethod
    def get_author_group_info(group_id, user_service):
        group = Author.objects.get_or_none(id=group_id)
#        if group:
#           return MultiAuthorGroupSerializer(group).data

        user_info_list = []

        if group:
            info = {
                'id': group.id,
                'creator_id': group.creator_id,
                'user_info': []
            }

            for user_id in group.members["user"]:
                member_id = user_id
                user = user_service.get_user(id=str(member_id))
                user_data = user_service.serialize(user)
                user_info_list.append(user_data)

            info['user_info'] = user_info_list
            return info
        else:
            return None

    @staticmethod
    def serialize(obj):
        return AuthorSerializer(obj).data

    @staticmethod
    def create_author_group(creator, user_list):
        author_group = Author.objects.create(creator_id=creator)
        author_group.add_group_member(user_list)
        author_group.save()
        return author_group

    @staticmethod
    def get_author_list_by_author_group(group_id):
        '''
        Gives the author list based on a group_id
        '''
        author_list = []
        author_group_member = Author.objects.get_or_none(id=group_id).members

        for user in author_group_member['user']:
            author_list.append(user)

        return author_list


class BookService(BaseService):

    @staticmethod
    def get_serializer():
        return BookSerializer

    @staticmethod
    def get_model():
        return Book

    @classmethod
    def serialize(cls, obj, context={}):
        return BookSerializer(obj, context=context).data

    @staticmethod
    def create_book(**kwargs):
        '''
        create book by args

        Returns:

            Book Object

        Raises:

            KeyError: If no creator_id or group_id in args

        '''

        CREATOR_ID, GROUP_ID = "creator_id", "group_id"
        AUTHOR = 'author'

        if not isinstance(kwargs[CREATOR_ID], str) and not isinstance(kwargs[CREATOR_ID], unicode):
            kwargs[CREATOR_ID] = kwargs[CREATOR_ID][0]

        if not isinstance(kwargs[GROUP_ID], str) and not isinstance(kwargs[GROUP_ID], unicode):
            kwargs[GROUP_ID] = kwargs[GROUP_ID][0]

        if AUTHOR not in kwargs:
            kwargs[AUTHOR] = ""

        if not (CREATOR_ID in kwargs and GROUP_ID in kwargs):
            raise KeyError
        else:
            book = Book.objects.create(**kwargs)
            book.save()
            return book

    @staticmethod
    def get_book(**kwagrs):
        return Book.objects.get_or_none(**kwagrs)

    @staticmethod
    def get_books(**kwagrs):
        return Book.objects.filter(**kwagrs)

    @staticmethod
    def delete_book(USER_ID, BOOK_ID):
        '''
        Delete a book by user_id and book_id
        Returns:
            delete: {Boolean}, if book is deleted
        Raises:
            Reference: if this user don't have this book
        '''
        ReferenceError_MSG = 'this user cannot delete this book'
        book = BookService.get_book(creator_id=USER_ID, id=BOOK_ID)
        if book:
            return book.delete()
        else:
            raise ReferenceError(ReferenceError_MSG)


@transaction.atomic
def _update_valid_fileds_by_dic(FIELDS, obj, DIC):
    valid_keys = filter(lambda k: k in FIELDS, DIC)
    obj = funcs.reduce(lambda o, k: setattr(o, k, DIC[k]), valid_keys, obj)
    obj.save()
    return obj

BOOK_FIELDS = ('avatar', 'book_name', 'author', 'page_format', 'preview_url',
               'cover', 'page_num', 'from_date', 'to_date', 'status')
update_book_field = partial(_update_valid_fileds_by_dic, BOOK_FIELDS)

ORDER_FIELDS = ('price', 'status', 'info')
update_order_field = partial(_update_valid_fileds_by_dic, ORDER_FIELDS)


def send_create_book_request_to_wxbook(book_id, group_id, creator_id):
    creator_token = UserService.get_auth_token(user_id=creator_id).key
 #   URL = 'http://192.168.0.126:8009/maili/book/{0}/typeset?group_id={1}'.format(book_id, group_id)
    URL = 'http://open.weixinshu.com/maili/book/{0}/typeset?group_id={1}'.format(book_id, group_id)
    response = requests.get(
        URL,
        headers={'Authorization': creator_token}
    )

    res = response.json()
    STATUS, SUCCESS, ERR_MSG = 'status', 'success', 'err_msg'
    if res[STATUS] == SUCCESS:
        return True
    else:
        raise ReferenceError(res[ERR_MSG])


def _delete_one_fields(book):
    DELETED = 'deleted'
    fields = [DELETED]

    def delete_books_fields(book):
        def delete_field(f):
            del book[f]
        return delete_field

    delete_book_one_field = delete_books_fields(book)

    map(lambda f: delete_book_one_field(f), fields)

    return book


def delete_book_list_some_field(books):
    new_books = map(_delete_one_fields, books)
    return new_books
