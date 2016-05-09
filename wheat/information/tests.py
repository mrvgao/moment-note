'''
Tests for utils.

@Author Minchiuan Gao <2016-May-9>
'''

from django.test import TestCase
import redis
from settings import REDIS_PUBSUB_TAG
from settings import REDIS_PUBSUB_DB
from information import redis_tools
from utils.utils import to_dict


class RedisUtilsTest(TestCase):
    def setUp(self):
        self.r = redis.StrictRedis(db=REDIS_PUBSUB_DB)
        self.p = self.r.pubsub()
        self.p.subscribe(redis_tools.get_channal_name())

    def test_get_channal_name(self):
        channal = redis_tools.get_channal_name()
        self.assertIsNotNone(channal)

    def test_pub_to_redis(self):
        message = {'code': '1101'}

        redis_tools._pub_to_redis(message)
        info = self.p.get_message()
        self.assertIsNotNone(info)  # subscribe success

        info = self.p.get_message()
        self.assertIsNotNone(info)   # get data

        self.assertIsNotNone(info['data'])
        self.assertTrue('code' in info['data'])
        info = self.p.get_message()
        self.assertIsNone(info)

    def test_publish_message(self):
        event = 'invitation'

        redis_tools.publish_message(event, 'sub_inv', 'hiruhkaf', 'i12hiur', {})

        info = self.p.get_message()
        self.assertIsNotNone(info)   # get data

        info = self.p.get_message()
        self.assertIsNotNone(info)
        self.assertTrue(str(info['data']).find(event) > 0)

    def test_publish_invitation(self):

        invitation = '2p193i1904ru'

        class Inviter:
            id = '12312'
            nickname = 'nickname'
            avatar = 'avatar'

        class Group:
            id = 1312
            name = 'haha'
            avatar = 'avatar'

        redis_tools.publish_invitation(invitation, Inviter(), Group(), 'father', '314afs', 'no')
        
        info = self.p.get_message()
        self.assertIsNotNone(info)   # get data

        info = self.p.get_message()
        self.assertIsNotNone(info)
        self.assertTrue(str(info['data']).find(invitation) > 0)



