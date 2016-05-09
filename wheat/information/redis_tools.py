# -*- coding:utf-8 -*-

import redis
from json import JSONEncoder
from settings import REDIS_PUBSUB_TAG
from settings import REDIS_PUBSUB_DB
from settings import REDIS_PUBSUB_CHANNEL
import random
import datetime
import threading
from apps.message.services import MessageService


def get_channal_name():
    return '{0}:{1}->'.format(REDIS_PUBSUB_TAG, REDIS_PUBSUB_CHANNEL)


def get_ramdon_code(message):
    message_len = len(str(message))
    t = datetime.datetime.now()
    seconds_str = "{:.9f}".format((t - datetime.datetime(1970, 1, 1)).total_seconds())
    random_num = random.randint(100, 999)
    # to avoid two client send message in the same time. Add a random number.

    code = str(message_len) + seconds_str.replace(".", "") + str(random_num)
    return code


def _pub_to_redis(message):
    r = redis.StrictRedis(db=REDIS_PUBSUB_DB)
    r.publish(get_channal_name(), JSONEncoder().encode(message))

    
def send_message_mannual(message_id):
    msg = MessageService.get_back_up(message_id)
    msg = msg.content
    publish_redis_message('', msg, create_mid=False)


def publish_invitation(invitation_id, inviter, group, role, invitee_id, msg):
    message = {
        'inviter': inviter.id,
        'inviter_nickname': inviter.nickname,
        'inviter_avatar': str(inviter.avatar),
        'group_id': group.id,
        'group_name': group.name,
        'group_avatar': str(group.avatar),
        'role': role,
        'invitee': invitee_id,
        'message': msg,
    }

    publish_message('invitation', 'sub_inv', invitation_id, invitee_id, message)
 
    
def publish_message(event, sub_event, invitation_id, receiver_id, message):
    message = {
        'event': event,
        'sub_event': sub_event,
        'invitation_id': invitation_id,
        'receiver_id': receiver_id,
        'message': message,
    }
    publish_redis_message(message)

    
def publish_redis_message(message, create_mid=True):
    code = get_ramdon_code(message)
    if not create_mid:
        _pub_to_redis(message)
    else:
        message['mid'] = code
        #pub_t = threading.Thread(target=_pub_to_redis, args=[message])
        #save_t = threading.Thread(
        #    target=MessageService.backup,
        #    args=[message, code, message['event'], message.get('sub_event', "")])

        _pub_to_redis(message)
        #pub_t.setDaemon(True)
        #save_t.setDaemon(True)

        #save_t.start()
        #pub_t.start()
