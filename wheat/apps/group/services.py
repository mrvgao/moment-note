# -*- coding:utf-8 -*-

from datetime import datetime
from django.db import transaction
from settings import REDIS_PUBSUB_DB

from customs.services import BaseService
from utils.redis_utils import publish_redis_message
from apps.user.services import UserService
from .models import Group, GroupMember, Invitation
from .serializers import GroupSerializer, GroupMemberSerializer, InvitationSerializer


class GroupService(BaseService):

    @classmethod
    def _get_model(cls, name='Group'):
        if name == 'Group':
            return Group
        elif name == 'GroupMember':
            return GroupMember
        elif name == 'Invitation':
            return Invitation

    @classmethod
    def get_serializer(cls, model='Group'):
        if model == 'Group':
            return GroupSerializer
        elif model == 'GroupMember':
            return GroupMemberSerializer
        elif model == 'Invitation':
            return InvitationSerializer


    @staticmethod
    def serialize_list(obj_list):
        if len(obj_list) > 0 and isinstance(obj_list[0], Group):
            return GroupSerializer(obj_list, many=True).data

    @classmethod
    def serialize(cls, obj, context={}):
        if isinstance(obj, Group):
            return GroupSerializer(obj, context=context).data
        elif isinstance(obj, GroupMember):
            return GroupMemberSerializer(obj, context=context).data
        elif isinstance(obj, Invitation):
            return InvitationSerializer(obj, context=context).data


    @staticmethod
    def get_all_friend_group(owner_id):
        ALL_FRIENDS = 'all_friends'
        
        user = UserService.get_user(id=owner_id)
        result = Group.objects.filter(creator_id=owner_id, group_type=ALL_FRIENDS)

        if user and len(result) == 0: # if this person no initial all friend group

            SELF = 'self'
            GroupService.create_group(
                creator=user, group_type=ALL_FRIENDS, name=ALL_FRIENDS, creator_role=SELF
            )

            result = Group.objects.filter(creator_id=owner_id, group_type=ALL_FRIENDS)

        return result

    @staticmethod
    def filter_group(**kwargs):
        return Group.objects.filter(**kwargs)

    @classmethod
    def get_group(cls, **kwargs):
        result =  Group.objects.get_or_none(**kwargs)
        return result

    @classmethod
    @transaction.atomic
    def create_group(cls, creator, group_type, name, creator_role=None):
        if not Group.valid_group_type(group_type) \
                or not GroupMember.valid_role(creator_role):
            return None
        group = Group.objects.create(
            creator_id=creator.id,
            group_type=group_type,
            name=name,
            admins={str(creator.id): {
                'name': creator.nickname,
                'joined_at': datetime.now()
            }},
            members={str(creator.id): {
                'name': creator.nickname,
                'joined_at': datetime.now(),
                'role': creator_role
            }})

        if creator_role is not None: 
            GroupMember.objects.create(
                member_id=creator.id,
                group_id=group.id,
                authority='admin',
                group_remark_name=name,
                avatar=creator.avatar,
                nickname=creator.nickname,
                role=creator_role)
        return group

    @classmethod
    @transaction.atomic
    def create_group_invitation(cls, group, inviter, invitation_dict):
        if not GroupMember.valid_role(invitation_dict['role'])\
                or str(inviter.id) not in group.members:
            return None
        message = {
            'inviter': inviter.id,
            'inviter_nickname': inviter.nickname,
            'inviter_avatar': str(inviter.avatar),
            'group_id': group.id,
            'group_name': group.name,
            'group_avatar': str(group.avatar),
            'role': invitation_dict['role'],
            'invitee': invitation_dict['invitee'],
            'message': invitation_dict['message'],
        }
        invitation = Invitation.objects.create(
            inviter=inviter.id,
            invitee=invitation_dict['invitee'],
            group_id=group.id,
            role=invitation_dict['role'],
            message=message)
        # send invitation
        message = {
            'event': 'invitation',
            'sub_event': 'sd_inv',  # send_invitation
            'invitation_id': invitation.id,
            'receiver_id': invitation_dict['invitee'],
            'message': message
        }

        # if user is registered
        publish_redis_message(REDIS_PUBSUB_DB, 'invitation->', message)
        return invitation

    @classmethod
    @transaction.atomic
    def add_group_member(cls, group, user, role):
        if not GroupMember.valid_role(role) \
                or user.id in group.members \
                or len(group.members) >= group.max_members:
            return False
        for member_id, member in group.members.items():
            if member['role'] == role and role != 'child':
                return False
        member_ids = group.members.keys()
        group.members[str(user.id)] = {
            'name': user.nickname,
            'joined_at': datetime.now(),
            'role': role
        }
        group.save()
        GroupMember.objects.create(
            member_id=user.id,
            group_id=group.id,
            group_remark_name=group.name,
            avatar=user.avatar,
            nickname=user.nickname,
            role=role)
        # group里所有成员建立“好友关系”
        UserService.create_friendships(str(user.id), member_ids)
        return True

    @classmethod
    def get_invitation(cls, **kwargs):
        return Invitation.objects.get_or_none(**kwargs)

    @classmethod
    @transaction.atomic
    def delete_invitation(cls, invitee, invitation):
        if str(invitee.id) != invitation.invitee:
            return False
        invitation.update(deleted=True)
        return True

    @classmethod
    @transaction.atomic
    def accept_group_invitation(cls, invitee, invitation):
        import pdb; pdb.set_trace()
        if str(invitee.phone) != invitation.invitee:
            return False
        group = GroupService.get_group(id=invitation.group_id)
        if GroupService.add_group_member(group, invitee, invitation.role):
            invitation.update(accepted=True, accept_time=datetime.now())
            # send invitation
            message = {
                'event': 'invitation',
                'sub_event': 'acc_inv_ntf',  # accept_invitation_notify
                'invitation_id': invitation.id,
                'receiver_id': invitation.inviter
            }
            publish_redis_message(REDIS_PUBSUB_DB, 'invitation->', message)
            return True
        return False

    @classmethod
    def get_user_group_ids(cls, user_id):
        group_ids = []
        ids = GroupMember.objects.filter(member_id=user_id, deleted=False).values_list('group_id', flat=True)
        for id in ids:
            group_ids.append(str(id))
        return group_ids
