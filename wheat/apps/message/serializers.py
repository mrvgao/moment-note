# -*- coding:utf-8 -*-

from customs.serializers import XModelSerializer
from .models import Message


class MessageSerializer(XModelSerializer):

    class Meta:
        model = Message
        fields = ('id', 'sender_id', 'receiver_id',
                  'chat_type', 'content_type', 'content',
                  'post_date', 'received',)
