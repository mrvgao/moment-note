# -*- coding:utf-8 -*-

from datetime import datetime
from django.db import transaction
from settings import REDIS_PUBSUB_DB

from customs.services import BaseService
from apps.user.services import UserService
from .models import MultiAuthorGroup, Book, Order
from .serializers import MultiAuthorGroupSerializer, BookSerializer, OrderSerializer
from customs.services import MessageService


class AuthorService:
    @staticmethod
    def get_serializer():
        return MultiAuthorGroupSerializer

    @staticmethod
    def get_model():
        return MultiAuthorGroup


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
