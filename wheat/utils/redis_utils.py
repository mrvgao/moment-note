# -*- coding:utf-8 -*-

import redis
from json import JSONEncoder
from settings import REDIS_PUBSUB_TAG
from settings import REDIS_PUBSUB_DB
import random
import datetime
import threading
from apps.message.services import MessageService


def get_ramdon_code(message):
    message_len = len(str(message))
    t = datetime.datetime.now()
    seconds_str= "{:.9f}".format((t - datetime.datetime(1970, 1, 1)).total_seconds())
    random_num = random.randint(100, 999)
    # to avoid two client send message in the same time. Add a random number.

    code = str(message_len) + seconds_str.replace(".", "")+ str(random_num)
    return code


def _pub_to_redis(channel, message):
    r = redis.StrictRedis(db=REDIS_PUBSUB_DB)
    r.publish(REDIS_PUBSUB_TAG + ':' + channel + '->', JSONEncoder().encode(message))


def publish_redis_message(channel, message):
    code = get_ramdon_code(message)
    message['mid'] = code

    pub_t = threading.Thread(target=_pub_to_redis, args=[channel, message])
    save_t = threading.Thread(
        target=MessageService.backup,
        args=[message, code, message['event'], message.get('sub_event', "")])

    pub_t.setDaemon(True)
    save_t.setDaemon(True)

    pub_t.start()
    save_t.start()
