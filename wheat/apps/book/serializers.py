# -*- coding:utf-8 -*-

from customs.serializers import XModelSerializer
from customs.fields import XImageField, DictStrField
from .models import MultiAuthorGroup, Book, Order


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

    remark_name = DictStrField(required=False, allow_blank=True)
    book_name = DictStrField(required=False, allow_blank=True)
    author = DictStrField(required=False, allow_blank=True)
    page_format = DictStrField(required=False, allow_blank=True)
    preview_url = DictStrField(required=False, allow_blank=True)

    class Meta:
        model = Book
        fields = ('id', 'creator_id', 'group_id'
                  'remark_name', 'avatar', 'book_name'
                  'author', 'page_format', 'preview_url'
                  'creator_at')


class OrderSerializer(XModelSerializer):

    class Meta:
        model = Order
        fields = ('id', 'book_id', 'price', 'status', 'creator_at', 'update_at')
