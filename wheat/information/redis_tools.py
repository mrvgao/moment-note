# -*- coding:utf-8 -*-

import redis
import random
import datetime
import threading
from apps.message.services import MessageService
from information.utils import RedisPubsub


def get_ramdon_code(message):
    message_len = len(str(message))
    t = datetime.datetime.now()
    seconds_str = "{:.9f}".format((t - datetime.datetime(1970, 1, 1)).total_seconds())
    random_num = random.randint(100, 999)
    # to avoid two client send message in the same time. Add a random number.

    code = str(message_len) + seconds_str.replace(".", "") + str(random_num)
    return code


def send_message_mannual(message_id):
    msg = MessageService.get_back_up(message_id)
    msg = msg.content
    publish_redis_message(msg, create_mid=False)


def publish_invitation(invitation, inviter, group, invitee, msg):
    message = {
        'inviter': invitation.inviter,
        'inviter_nickname': inviter.nickname,
        'inviter_avatar': str(inviter.avatar),
        'group_id': group.id,
        'group_name': group.name,
        'group_avatar': str(group.avatar),
        'role': invitation.role,
        'invitee': invitee.id,
        'message': msg,
    }

    publish_invite_message('invitation', 'sub_inv', invitation.id, invitee.id, message)
 
    
def accept_invitation(invitation, invitee_id):
    message = {
        'event': 'invitation',
        'sub_event': 'acc_inv_ntf',  # accept_invitation_notify
        'invitation_id': invitation.id,
        'receiver_id': invitation.inviter,
        'invitee': str(invitee_id)
    }

    publish_redis_message(message)


def publish_delete_friend(receiver_id, friend_id):
    message = {
        'event': 'delete',
        'sub_event': 'friend',
        'receiver_id': receiver_id,
        'friend_id': friend_id
    }
    publish_redis_message(message)

    
def publish_invite_message(event, sub_event, invitation_id, receiver_id, message):
    message = {
        'event': event,
        'sub_event': sub_event,
        'invitation_id': invitation_id,
        'receiver_id': receiver_id,
        'message': message,
    }
    publish_redis_message(message)


def publish_book_message(receiver_id, book_id, book_data):
    message = {
        'book_id': book_id,
        'receiver_id': receiver_id,
        'event': 'book',
        'book': book_data
    }

    publish_redis_message(message)


def publish_moment_message(moment_id, sender_id, receiver_id):
    message = {
        'sender': sender_id,
        'moment_id': moment_id,
        'receiver_id': receiver_id,
        'event': 'moment'
    }

    publish_redis_message(message)

    
def publish_redis_message(message, create_mid=True):
    code = get_ramdon_code(message)
    if not create_mid:
        RedisPubsub.pub(message)
    else:
        message['mid'] = code
        RedisPubsub.pub(message)
        MessageService.backup(message, code, message['event'], message.get('sub_event', ""))
