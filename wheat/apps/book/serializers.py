# -*- coding:utf-8 -*-

from customs.serializers import XModelSerializer
from customs.fields import XImageField, DictStrField
from .models import MultiAuthorGroup, Book, Order
from rest_framework import serializers


class MultiAuthorGroupSerializer(XModelSerializer):
    class Meta:
        model = MultiAuthorGroup
        fields = ('id', 'creator_id', 'created_at', 'members')


class BookSerializer(XModelSerializer):
    avatar = XImageField(
        max_length=100,
        allow_empty_file=False,
        required=False,
        use_url=True,
        style={'input_type': 'file'}
    )

    remark_name = serializers.CharField(required=False, allow_blank=True)
    book_name = serializers.CharField(required=False, allow_blank=True)
    author = serializers.CharField(required=False, allow_blank=True)
    page_format = serializers.CharField(required=False, allow_blank=True)
    preview_url = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = Book
        fields = ('id', 'creator_id', 'group_id',
                  'remark_name', 'avatar', 'book_name',
                  'author', 'page_format', 'preview_url',
                  'created_at')


class OrderSerializer(XModelSerializer):

    class Meta:
        model = Order
        fields = ('id', 'book_id', 'price', 'status', 'created_at', 'update_at')
