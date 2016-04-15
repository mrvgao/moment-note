# -*- coding:utf-8 -*-

import redis
from optparse import make_option
from json import JSONDecoder, JSONEncoder
from django.core.management.base import BaseCommand
from django.db import connection
from settings import REDIS_PUBSUB_DB, REDIS_PUBSUB_TAG

from apps.message.services import MessageService, GroupMessageService
from utils import redis_utils


def listen_on_redis_pubsub():
    r = redis.StrictRedis(db=REDIS_PUBSUB_DB)
    p = r.pubsub(ignore_subscribe_messages=True)
    CHAT = 'chat'

    p.subscribe(REDIS_PUBSUB_TAG + ":->" + CHAT)
    for m in p.listen():
        print 'receive message:', m
        message = JSONDecoder().decode(m['data'])
        if _message_valid(message):
            redis_utils.publish_redis_message(CHAT, message)

        connection.close()


def _message_valid(messaege):
    if messaege['event'] == 'chat' and messaege['sub_event'] in ['p2p', 'p2g']:
        return True
    else:
        return False


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
