# -*- coding:utf-8 -*-

import redis
from json import JSONEncoder


def publish_redis_message(redis_db, channel, message):
    r = redis.StrictRedis(db=redis_db)
    r.publish(channel, JSONEncoder().encode(message))
