# -*- coding:utf-8 -*-

from django.db import transaction
from django.db.models import Q

from customs.services import BaseService
from .models import Message
from .serializers import MessageSerializer


class MessageService(BaseService):

    @classmethod
    def _get_model(cls, name='Message'):
        if name == 'Message':
            return Message

    @classmethod
    def get_serializer(cls, model='Message'):
        if model == 'Message':
            return MessageSerializer

    @classmethod
    def serialize(cls, obj, context={}):
        if isinstance(obj, Message):
            return MessageSerializer(obj, context=context).data

    @classmethod
    def get_message(cls, **kwargs):
        return Message.objects.get_or_none(**kwargs)

    @classmethod
    def get_messages(cls, **kwargs):
        return Message.objects.filter(**kwargs)

    @classmethod
    @transaction.atomic
    def create_message(cls, message_dict):
        sender_id = message_dict.get('sender_id')
        receiver_id = message_dict.get('receiver_id')
        chat_type = message_dict.get('chat_type')
        content_type = message_dict.get('content_type')
        content = message_dict.get('content')
        if sender_id and receiver_id \
                and Message.valid_chat_type(chat_type) \
                and Message.valid_content_type(content_type) \
                and Message.valid_content(content):
            message = Message.objects.create(
                sender_id=sender_id,
                receiver_id=receiver_id,
                chat_type=chat_type,
                content_type=content_type,
                content=content)
            return message
        return None

    @classmethod
    @transaction.atomic
    def update_message_as_received(cls, message):
        if not message.received:
            message.update(received=True)

    @classmethod
    @transaction.atomic
    def update_messages_as_received(cls, message_ids):
        Message.objects.filter(id__in=message_ids,
                               received=False).update(received=True)

    @classmethod
    def get_session_unreceived_messages(cls, sender_id, receiver_id):
        messages = Message.objects.filter(
            receiver_id=receiver_id,
            received=False).order_by('post_date')[:1]
        if not messages:
            return []
        messages = Message.objects.filter(
            Q(Q(sender_id=sender_id) & Q(receiver_id=receiver_id)) |
            Q(Q(sender_id=receiver_id) & Q(receiver_id=sender_id)),
            post_date__gte=messages[0].post_date).order_by('post_date')
        return list(messages)

    @classmethod
    def get_user_unreceived_messages(cls, receiver_id):
        senders = set(Message.objects.filter(received=False).
                      values_list('sender_id', flat=True))
        messages = []
        for sender_id in senders:
            messages += MessageService.get_session_unreceived_messages(sender_id, receiver_id)
        return messages
