# -*- coding:utf-8 -*-

from datetime import datetime
from django.db import transaction
from customs.services import BaseService
from apps.user.services import UserService
from apps.user.services import FriendshipService
from .models import Group, GroupMember, Invitation
from .serializers import GroupSerializer, GroupMemberSerializer, InvitationSerializer
from customs.services import MessageService
from customs.services import role_map
from apps.moment.services import MomentService
from customs.api_tools import api
from utils.redis_utils import publish_redis_message
from information import redis_tools


class GroupService(BaseService):

    model = Group
    serializer = GroupSerializer

    @api
    def create(self, creator_id, group_type, creator_role=None, name=None):
        creator_role = creator_role or 'self'
        name = name or group_type

        group = super(GroupService, self).create(
            creator_id=creator_id,
            group_type=group_type,
            name=name
        )

        GroupMemberService().create(creator_id, group.id, creator_role)

        return group

    def create_default_home(self, user_id):
        ALL_HOME = 'all_home_member'
        return self.create(user_id, ALL_HOME)

    def valid_role(self, r):
        if r.startswith('r-'):
            return r[2:] in role_map
        return r in role_map

    def group_type_valid(self, group_type):
        return Group.valid_group_type(group_type)

    @api
    def get(self, owner_id, keyword):
        return super(GroupService, self).get(creator_id=owner_id, group_type=keyword)
        
    @classmethod
    @transaction.atomic
    def create_group_invitation(cls, group, inviter, invitee_phone, role, append_msg):
        if not _valid_role(role) \
                or str(inviter.id) not in group.members:
            return None

        invitation = Invitation.objects.create(
            inviter=inviter.id,
            invitee=invitee_phone,
            group_id=group.id,
            role=role,
            message=append_msg)
        # send invitation

        invitee = UserService.get_user(phone=invitee_phone)

        if invitee:
            # if user is registered send to redis
            redis_tools.publish_invitation(
                invitation_id=invitation.id,
                inviter=inviter,
                group=group.id,
                role=role,
                invitee_id=invitee.id,
                msg=append_msg,
            )

        MessageService.send_invitation(
            phone=invitee_phone,
            inviter_phone=inviter.phone,
            inviter_nickname=inviter.nickname,
            message=str(append_msg).strip(),
            role=role,
        )

        return invitation

    @classmethod
    @transaction.atomic
    def add_group_member(cls, group, user, role):
        if not _valid_role(role):
            raise NameError(role)
        elif user.id in group.members and user.id != group.creator_id:
            raise ReferenceError(user.id)
        elif len(group.members) >= group.max_members:
            raise IndexError('reach the max member number of group')
        elif _role_duplicate(group, role):
            raise KeyError(role)

        # member_ids = group.members.keys()
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
        # if not role.startswith('r-'):
        # UserService.create_friendships(str(user.id), [])

        return True

    @staticmethod
    def get_home_member(user_id):
        try:
            home_member = Group.get_home_member(user_id)
            return home_member
        except Exception as e:
            raise e

    @classmethod
    def get_invitation(cls, **kwargs):
        return Invitation.objects.get_or_none(**kwargs)

    @classmethod
    @transaction.atomic
    def delete_invitation(cls, invitee, invitation):
        if str(invitee.phone) != invitation.invitee:
            return False
        invitation.update(deleted=True)
        return True

    @classmethod
    @transaction.atomic
    def add_person_to_user_group(cls, host_id, new_member_id, role, group_type='all_home_member'):
        host_group_id = GroupService.get_group_if_without_create(host_id, group_type)
        host_group = GroupService.get_group(id=host_group_id)
        new_member_obj = UserService.get_user(id=new_member_id)
        GroupService.add_group_member(host_group, new_member_obj, role)

    @staticmethod
    @transaction.atomic
    def accept_group_invitation(invitee, invitation):
        '''
        If invitee is already is his gorup member.
        Raises:
            ReferenceError When invitation.invitee value is not same as invitee.phone, which means this use not login.
        '''
        GroupService.add_person_to_user_group(
                    host_id=str(invitee.id),
                    new_member_id=str(invitation.inviter),
                    role='r-'+invitation.role
        )

        GroupService.add_person_to_user_group(
                    host_id=str(invitation.inviter),
                    new_member_id=str(invitee.id),
                    role=invitation.role
        )
        invitation.update(accepted=True, accept_time=datetime.now())
        FriendshipService.create_friendship(str(invitee.id), str(invitation.inviter))
        message = {
                    'event': 'invitation',
                    'sub_event': 'acc_inv_ntf',  # accept_invitation_notify
                    'invitation_id': invitation.id,
                    'receiver_id': invitation.inviter,
                    'invitee': str(invitee.id)
        }
        publish_redis_message('invitation', message)

    @classmethod
    def get_user_group_ids(cls, user_id):
        group_ids = []
        ids = GroupMember.objects.filter(member_id=user_id, deleted=False).values_list('group_id', flat=True)
        for id in ids:
            group_ids.append(str(id))
        return group_ids

    @staticmethod
    def delete_person_from_each_group(host_id, member_id):
        GroupService.delete_from_host(host_id=host_id, member_id=member_id)
        GroupService.delete_from_host(host_id=member_id, member_id=host_id)
        FriendshipService.delete_friendship(host_id, member_id)
        message = {
            'event': 'delete',
            'sub_event': 'friend',
            'receiver_id': member_id,
            'friend_id': host_id
        }
        publish_redis_message('test', message)

    @staticmethod
    def delete_from_host(host_id, member_id):
        host_group = GroupService.get_group(creator_id=host_id)
        host_group.delete_home_member(member_id)
        GroupService.delete_from_group_member(host_group.id, member_id)
        return host_group.id

    @staticmethod
    def delete_from_group_member(group_id, member):
        try:
            group_m = GroupMember.objects.get(group_id=group_id, member_id=member)
            if group_m:
                return group_m.delete()
        except Exception as e:
            print e
            return False


def _get_all_friend_home_id(user_id):
    group_ids = list(GroupMember.objects.filter(member_id=user_id, deleted=False).values_list('group_id', flat=True))
    return group_ids
    # A_H_M = 'all_home_member'
    # group = GroupService.get_group(creator_id=user_id, group_type=A_H_M)
    # if group:
    #     return group.id
    # else:
    #     return None


def _add_friend(friends_list, group_id):
    try:
        group = GroupService.get_group(id=group_id)
        map(lambda members_id: friends_list.append(members_id), group.members)
    except Exception:
        print 'group not exist'
    return friends_list


def get_friend_from_group_id(group_id_list, user_id):
    friend_list = []
    reduce(_add_friend, group_id_list, friend_list)
    return filter(lambda id: id != user_id, friend_list)


def get_all_home_member_list(user_id):
    all_home_group_ids = _get_all_friend_home_id(user_id)
    return get_friend_from_group_id(all_home_group_ids, user_id)


def __get_avatar(user_id):
    try:
        return str(UserService.get_user(id=user_id).avatar)
    except Exception as e:
        print e
        return None


def __get_activity(u):
    m_id, date = MomentService.get_recent_moment(u)
    return {'moment_id': m_id, 'date': date}


def _set_avatar(group):
    return lambda u: group.members[u].setdefault('avatar', __get_avatar(u))


def _set_activity(group):
    return lambda u: group.members[u].setdefault('activity', __get_activity(u))


def _action_on_group_member(group, func):
    map(func(group), group.members)
    return group


def add_group_info(groups, func):
    map(lambda g: _action_on_group_member(g, func), groups)
    return groups


def get_group_member_avatar(groups):
    return add_group_info(groups,  _set_avatar)


def get_group_member_activity(groups):
    return add_group_info(groups,  _set_activity)


def _valid_role(r):
    if r.startswith('r-'):
        return r[2:] in role_map
    return r in role_map


def _role_duplicate(group, role):
    could_deplicate_roles = ['son', 'daughter', 'slibe', 'sister']
    if role in could_deplicate_roles or role.startswith('r-'):
        return False
    else:
        for _, info in group.members.iteritems():
            if info['role'] == role:
                return True
        return False


class GroupMemberService(BaseService):
    
    model = GroupMember
    serializer = GroupMemberSerializer
    
    def create(self, uid, group_id, role, name='', remark='', avatar='', nickname='', authority='admin'):
        member = super(GroupMemberService, self).create(
                member_id=uid,
                group_id=group_id,
                authority=authority,
                group_remark_name=name,
                avatar=avatar,
                nickname=nickname,
                role=role)

        return member
        

class InvitationService(BaseService):

    model = Invitation
    serializer = InvitationSerializer

    def create(self):
        pass
