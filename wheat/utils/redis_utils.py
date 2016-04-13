# -*- coding:utf-8 -*-

import redis
from json import JSONEncoder
from settings import REDIS_PUBSUB_TAG
import random
import datetime
import threading
from apps.message.services import MessageService


def get_ramdon_code(message):
    message_len = len(str(message))
    t = datetime.datetime.now()
    seconds = (t-datetime.datetime(1970, 1, 1)).total_seconds()
    random_num = random.randint(0, 100)

    COMMA_LEN = 4
    code = str(message_len) + str(seconds)[:-1 * COMMA_LEN] + str(random_num)
    return code


def _pub_to_redis(redis_db, channel, message):
    r = redis.StrictRedis(db=redis_db)
    r.publish(REDIS_PUBSUB_TAG + ':' + channel, JSONEncoder().encode(message))


def publish_redis_message(redis_db, channel, message):
    code = get_ramdon_code(message)
    message['uid'] = code

    pub_t = threading.Thread(target=_pub_to_redis, args=[redis_db, channel, message])
    save_t = threading.Thread(target=MessageService.backup, args=[message, code])

    pub_t.setDaemon(True)
    save_t.setDaemon(True)

    pub_t.start()
    save_t.start()

