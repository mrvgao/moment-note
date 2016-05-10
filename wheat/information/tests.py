'''
Tests for utils.

@Author Minchiuan Gao <2016-May-9>
'''

from django.test import TestCase
from information import redis_tools
from collections import namedtuple
from information.utils import RedisPubsub
from information.utils import get_channal_name
from apps.message.models import MessageBackup
import time


class RedisUtilsTest(TestCase):
    def test_get_channal_name(self):
        channal = get_channal_name()
        self.assertIsNotNone(channal)

    def test_pub_to_redis(self):
        message = {'code': '1101'}

        RedisPubsub.pub(message)
        info = RedisPubsub.get()
        self.assertIsNotNone(info)  # subscribe success

        info = RedisPubsub.get()
        self.assertIsNotNone(info)   # get data

        self.assertIsNotNone(info['data'])
        self.assertTrue('code' in info['data'])
        info = RedisPubsub.get()
        self.assertIsNone(info)

    def test_publish_invite_message(self):
        event = 'invitation'

        redis_tools.publish_invite_message(event, 'sub_inv', 'hiruhkaf', 'i12hiur', {})

        info = RedisPubsub.get()
        self.assertIsNotNone(info)
        self.assertTrue(str(info['data']).find(event) > 0)
        message = MessageBackup.objects.get(event=event)
        self.assertEqual(message.sub_event, 'sub_inv')

    def test_publish_invitation(self):

        invitation = '2p193i1904ru'

        Inviter = namedtuple('Inviter', ['id', 'nickname', 'avatar'])
        Group = namedtuple('Group', ['id', 'name', 'avatar'])
        Invitee = namedtuple('Invitee', ['id'])
        Invitation = namedtuple('Invitation', ['id', 'inviter', 'nickname', 'role'])

        invitation = Invitation('inv-id', 'inviter', 'nickname', 'father')
        inviter = Inviter('some-id', 'nickname', '/pic.jpg')
        invitee = Invitee('some-invitee-id')
        group = Group('group-id', 'group', 'avatar')

        redis_tools.publish_invitation(invitation, inviter, group, invitee, 'no')
        
        info = RedisPubsub.get()
        self.assertIsNotNone(info)
        self.assertTrue(str(info['data']).find('invitation') > 0)
