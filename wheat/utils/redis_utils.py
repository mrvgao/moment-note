# -*- coding:utf-8 -*-

import redis
from json import JSONEncoder
from settings import REDIS_PUBSUB_TAG


def publish_redis_message(redis_db, channel, message):
    r = redis.StrictRedis(db=redis_db)
    r.publish(REDIS_PUBSUB_TAG + ':' + channel, JSONEncoder().encode(message))
