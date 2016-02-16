# -*- coding:utf-8 -*-

import redis
from optparse import make_option
from json import JSONDecoder, JSONEncoder
from django.core.management.base import BaseCommand
from settings import REDIS_PUBSUB_DB

from apps.message.services import MessageService, GroupMessageService


def listen_on_redis_pubsub():
    r = redis.StrictRedis(db=REDIS_PUBSUB_DB)
    p = r.pubsub(ignore_subscribe_messages=True)
    p.subscribe("->chat")
    for m in p.listen():
        print 'receive message:', m
        message_dict = JSONDecoder().decode(m['data'])
        if message_dict['event'] == 'chat':
            if message_dict['sub_event'] == 'p2p':
                message = MessageService.create_message(message_dict)
                if message:
                    print 'push message:', message.id
                    message = MessageService.serialize(message)
                    message['event'] = 'chat'
                    message['sub_event'] = 'p2p'
                    r.publish('chat->', JSONEncoder().encode(message))
            elif message_dict['sub_event'] == 'p2g':
                messages = GroupMessageService.create_messages(message_dict)
                if messages:
                    for message in messages:
                        print 'push message:', message.id
                        message = GroupMessageService.serialize(message)
                        message['event'] = 'chat'
                        message['sub_event'] = 'p2g'
                        r.publish('chat->', JSONEncoder().encode(message))
        elif message_dict['event'] == 'receive_messages':
            p2p_message_ids = message_dict.get('p2p_message_ids')
            if p2p_message_ids:
                MessageService.update_messages_as_received(p2p_message_ids)
            p2g_message_ids = message_dict.get('p2g_message_ids')
            if p2g_message_ids:
                GroupMessageService.update_messages_as_received(p2g_message_ids)
        elif message_dict['event'] == 'get_unreceived_messages':
            receiver_id = message_dict['receiver_id']
            p2p_messages = MessageService.get_user_unreceived_messages(receiver_id)
            p2p_messages = MessageService.serialize_objs(p2p_messages)
            p2g_messages = GroupMessageService.get_user_unreceived_messages(receiver_id)
            p2g_messages = GroupMessageService.serialize_objs(p2g_messages)
            message_dict = {
                'event': message_dict['event'],
                'p2p_messages': p2p_messages,
                'p2g_messages': p2g_messages,
                'receiver_id': receiver_id
            }
            print 'get unreceived p2p messages of', receiver_id, ':', p2p_messages
            print 'get unreceived p2g messages of', receiver_id, ':', p2g_messages
            r.publish('chat->', JSONEncoder().encode(message_dict))


class Command(BaseCommand):
    help = u'Manages Account'

    option_list = BaseCommand.option_list + (
        make_option('--usage',
                    action='help',
                    help='python manage.py listen_chat --redis'),
        make_option('--redis',
                    action='store_true',
                    dest='redis',
                    default=False,
                    help='listen on redis'),
    )

    def handle(self, *args, **options):
        if options['redis']:
            print 'listen on redis pub/sub'
            listen_on_redis_pubsub()
