# -*- coding:utf-8 -*-

import redis
import logging
from optparse import make_option
from json import JSONDecoder, JSONEncoder
from django.core.management.base import BaseCommand
from django.db import connection
from settings import REDIS_PUBSUB_DB, REDIS_PUBSUB_TAG
from utils import redis_utils

from apps.user.services import UserService

logger = logging.getLogger('pubsub')


def listen_on_redis_pubsub():
    r = redis.StrictRedis(db=REDIS_PUBSUB_DB)
    p = r.pubsub(ignore_subscribe_messages=True)
    p.subscribe(REDIS_PUBSUB_TAG + ":->login")
    for m in p.listen():
        logger.info('receive message: {0}'.format(m))
        login_data = JSONDecoder().decode(m['data'])
        user_id = login_data.get('user_id')
        token = login_data.get('token')

        data = {
                'event': 'login',
                'login': True,
                'receiver_id': user_id,
        }
        if UserService.check_auth_token(user_id, token):
            user = UserService.get_user(id=user_id)
            data['user'] = UserService.serialize(user)
        else:
            data['login'] = False

        redis_utils.publish_redis_message('', data)
        connection.close()


class Command(BaseCommand):
    help = u'Manages Account'

    option_list = BaseCommand.option_list + (
        make_option('--usage',
                    action='help',
                    help='python manage.py listen_login --redis'),
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
