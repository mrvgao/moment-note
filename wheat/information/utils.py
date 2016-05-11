'''
Utils for information. 
'''
import redis
from settings import REDIS_PUBSUB_TAG
from settings import REDIS_PUBSUB_DB
from settings import REDIS_PUBSUB_CHANNEL
from json import JSONEncoder


def get_channal_name():
    return '{0}:{1}->'.format(REDIS_PUBSUB_TAG, REDIS_PUBSUB_CHANNEL)


class RedisPubsub(object):
    r = redis.StrictRedis(db=REDIS_PUBSUB_DB)
    p = r.pubsub()
    p.subscribe(get_channal_name())

    @staticmethod
    def get():
        return RedisPubsub.p.get_message()

    @staticmethod
    def pub(message):
        RedisPubsub.r.publish(
            get_channal_name(),
            JSONEncoder().encode(message)
        )
        
