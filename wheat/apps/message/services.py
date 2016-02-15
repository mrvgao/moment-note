# -*- coding:utf-8 -*-

from django.db import transaction
from django.db.models import Q
import uuid

from customs.services import BaseService
from apps.group.services import GroupService
from .models import Message, GroupMessage
from .serializers import MessageSerializer, GroupMessageSerializer


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
        content_type = message_dict.get('content_type')
        content = message_dict.get('content')
        if sender_id and receiver_id \
                and Message.valid_content_type(content_type) \
                and Message.valid_content(content):
            message = Message.objects.create(
                sender_id=sender_id,
                receiver_id=receiver_id,
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
        Message.objects.filter(
            id__in=message_ids,
            received=False).update(received=True)

    @classmethod
    def get_session_unreceived_messages(cls, sender_id, receiver_id):
        ''' 获取某次会话中，第一条未接收到的消息之后的所有收发消息 '''
        messages = Message.objects.filter(
            sender_id=sender_id,
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
        ''' 获取某个用户的所有未接受到的消息 '''
        senders = set(Message.objects.filter(
            receiver_id=receiver_id,
            received=False).values_list('sender_id', flat=True))
        messages = []
        for sender_id in senders:
            messages += MessageService.get_session_unreceived_messages(
                sender_id, receiver_id)
        return messages


class GroupMessageService(BaseService):

    @classmethod
    def _get_model(cls, name='GroupMessage'):
        if name == 'GroupMessage':
            return GroupMessage

    @classmethod
    def get_serializer(cls, model='GroupMessage'):
        if model == 'GroupMessage':
            return GroupMessageSerializer

    @classmethod
    def serialize(cls, obj, context={}):
        if isinstance(obj, GroupMessage):
            return GroupMessageSerializer(obj, context=context).data

    @classmethod
    def get_message(cls, **kwargs):
        return GroupMessage.objects.get_or_none(**kwargs)

    @classmethod
    def get_messages(cls, **kwargs):
        return GroupMessage.objects.filter(**kwargs)

    @classmethod
    @transaction.atomic
    def create_messages(cls, message_dict):
        ''' group里面除sender之外的所有成员都会创建一条新消息 '''
        sender_id = message_dict.get('sender_id')
        group_id = message_dict.get('group_id')
        content_type = message_dict.get('content_type')
        content = message_dict.get('content')
        if sender_id and group_id \
                and GroupMessage.valid_content_type(content_type) \
                and GroupMessage.valid_content(content):
            group = GroupService.get_group(id=group_id)
            messages = []
            if not group:
                return messages
            for member_id, member_info in group.members.items():
                if member_id == sender_id:
                    continue
                message = GroupMessage(
                    id=uuid.uuid4(),
                    sender_id=sender_id,
                    group_id=group_id,
                    receiver_id=member_id,
                    content_type=content_type,
                    content=content)
                messages.append(message)
            GroupMessage.objects.bulk_create(messages)
            return messages
        return []

    @classmethod
    @transaction.atomic
    def update_message_as_received(cls, message):
        if not message.received:
            message.update(received=True)

    @classmethod
    @transaction.atomic
    def update_messages_as_received(cls, message_ids):
        GroupMessage.objects.filter(
            id__in=message_ids,
            received=False).update(received=True)

    @classmethod
    def get_session_unreceived_messages(cls, group_id, receiver_id):
        ''' 获取某个群会话中从第一条未接收的消息之后的所有群消息 '''
        messages = GroupMessage.objects.filter(
            group_id=group_id,
            receiver_id=receiver_id,
            received=False).order_by('post_date')[:1]
        if not messages:
            return []
        messages = GroupMessage.objects.filter(
            group_id=group_id,
            post_date__gte=messages[0].post_date).order_by('post_date')
        return list(messages)

    @classmethod
    def get_user_unreceived_messages(cls, receiver_id):
        ''' 获取所有未接收到的群消息 '''
        group_ids = set(GroupMessage.objects.filter(
            receiver_id=receiver_id,
            received=False).values_list('group_id', flat=True))
        messages = []
        for group_id in group_ids:
            messages += GroupMessageService.get_session_unreceived_messages(
                group_id, receiver_id)
        return messages
