# -*- coding:utf-8 -*-

from customs.serializers import XModelSerializer
from .models import Message, GroupMessage


class MessageSerializer(XModelSerializer):

    class Meta:
        model = Message
        fields = ('id', 'sender_id', 'receiver_id',
                  'content_type', 'content',
                  'post_date', 'received',)


class GroupMessageSerializer(XModelSerializer):

    class Meta:
        model = GroupMessage
        fields = ('id', 'sender_id', 'group_id', 'receiver_id',
                  'content_type', 'content',
                  'post_date', 'received',)
