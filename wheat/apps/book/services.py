# -*- coding:utf-8 -*-

from datetime import datetime
from django.db import transaction
from settings import REDIS_PUBSUB_DB

from customs.services import BaseService
from apps.user.services import UserService
from .models import MultiAuthorGroup, Book, Order
from .serializers import MultiAuthorGroupSerializer, BookSerializer, OrderSerializer
from customs.services import MessageService
import ast


class AuthorService:
    @staticmethod
    def get_serializer():
        return MultiAuthorGroupSerializer

    @staticmethod
    def get_model():
        return MultiAuthorGroup

    @staticmethod
    def get_author_group(group_id):
        group = MultiAuthorGroup.objects.get_or_none(id=group_id)
        if group:
            return MultiAuthorGroupSerializer(group).data
        else:
            return None

    @staticmethod
    def serialize(obj):
        return MultiAuthorGroupSerializer(obj).data

    @staticmethod
    def create_author_group(creator, user_list):
        author_group = MultiAuthorGroup.objects.create(creator_id=creator)
        author_group.add_group_member(user_list)
        author_group.save()
        return author_group

    @staticmethod
    def get_author_list_by_author_group(group_id):
        '''
        Gives the author list based on a group_id
        '''
        author_list = []
        author_group_member = MultiAuthorGroup.objects.get_or_none(id=group_id).members

        for user in author_group_member:
            author_list.append(str(author_group_member[user]['user_id']))

        return author_list



class BookService:
    @staticmethod
    def get_serializer():
        return BookSerializer

    @staticmethod
    def get_model():
        return Book


class OrderService:
    @staticmethod
    def get_serializer():
        return OrderSerializer

    @staticmethod
    def get_model():
        return Order
