# -*- coding:utf-8 -*-

import redis
from optparse import make_option
from json import JSONDecoder, JSONEncoder

from django.core.management.base import BaseCommand

from apps.message.services import MessageService


def listen_on_redis_pubsub():
    r = redis.StrictRedis(db=2)
    p = r.pubsub(ignore_subscribe_messages=True)
    p.subscribe(">p2p")
    for m in p.listen():
        print 'receive message:', m
        message_dict = JSONDecoder().decode(m['data'])
        if message_dict['event'] == 'p2p':
            message = MessageService.create_message(message_dict)
            print 'push message:', message.id
            r.publish('p2p<', JSONEncoder().encode(MessageService.serialize(message)))
        elif message_dict['event'] == 'receive_messages':
            message_ids = message_dict['message_ids']
            MessageService.update_messages_as_received(message_ids)
        elif message_dict['event'] == 'get_unreceived_messages':
            receiver_id = message_dict['receiver_id']
            messages = MessageService.get_user_unreceived_messages(receiver_id)
            messages = MessageService.serialize_objs(messages)
            message_dict = {
                'event': message_dict['event'],
                'messages': messages,
                'receiver_id': receiver_id
            }
            print 'get unreceived messages of', receiver_id, ':', messages
            r.publish('p2p<', JSONEncoder().encode(message_dict))


class Command(BaseCommand):
    help = u'Manages Account'

    option_list = BaseCommand.option_list + (
        make_option('--usage',
                    action='help',
                    help='python manage.py listen_message --redis'),
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
