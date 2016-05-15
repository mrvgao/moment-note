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
from information import redis_tools
from customs.delegates import delegate
from . import roles


class GroupService(BaseService):

    model = Group
    serializer = GroupSerializer

    ALL_HOME = 'all_home_member'

    class MemberInfo(object):
        def __init__(self, role=None):
            SELF = 'self'
            self.role = role or SELF
            self.joined_at = datetime.now()

        @property
        def info(self):
            return {
                'joined_at': self.joined_at,
                'role': self.role,
            }

    @api
    def create(self, creator_id, group_type, creator_role=None, name=None):
        creator_role = creator_role or 'self'
        name = name or group_type

        group = super(GroupService, self).create(
            creator_id=creator_id,
            group_type=group_type,
            name=name
        )

        self.add_group_member(group, creator_id)
        self.add_group_admin(group, creator_id)

        return group

    def create_default_home(self, user_id):
        return self.create(user_id, GroupService.ALL_HOME)

    def valid_role_name(self, r):
        if r.startswith('r-'):
            return r[2:] in role_map
        return r in role_map

    def role_is_valid(self, group, role):
        # test if role name is valid;
        valid_name = self.valid_role_name(role)
        # test if role is single, test if group already has this role.
        role_acceptable = self.role_acceptable(group, role)
        return valid_name and role_acceptable

    def role_acceptable(self, group, role):
        role_mutiple = roles.is_mutiple(role)
        if not role_mutiple and self.consist_role(group.id, role):
            return False
        else:
            return True

    def group_type_valid(self, group_type):
        return Group.valid_group_type(group_type)

    @api
    def get_home(self, owner_id):
        return self.get(creator_id=owner_id, group_type=GroupService.ALL_HOME)
        
    def consist_role(self, group_id, role):
        group = super(GroupService, self).get(id=group_id)

        have = False
        for _, user in group.members.iteritems():
            if user['role'] == role:
                have = True

        return have
        
    def consist_member(self, group_id, **kwargs):
        user_id = UserService().get(**kwargs).id
        group = super(GroupService, self).get(id=group_id)
        member_record = GroupMemberService().get(group_id=group_id, member_id=user_id)

        consist = False
        
        if str(user_id) in group.members:
            if member_record and not member_record.deleted:
                consist = True

        return consist

    @transaction.atomic
    def _add_group_person(self, group, character, user_id, role=None):
        assert group is not None, 'cannot add ' + user_id + 'to None Group'

        member_info = GroupService.MemberInfo(role).info

        # need check if this role could be add in!
        getattr(group, character)[str(user_id)] = member_info

        GroupMemberService().create(group, user_id, character, member_info['role'])
        FriendshipService().create(str(group.creator_id), str(user_id))
        
        # set group member by character. 
        group.save()
        return getattr(group, character)

    def add_group_member(self, group, user_id, role=None):
        return self._add_group_person(group, 'members', user_id, role)

    def add_group_admin(self, group, user_id):
        return self._add_group_person(group, 'admins', user_id)
    
    def delete_member(self, group, member_id):
        group.members.pop(str(member_id), None)
        group.save()

        GroupMemberService().delete(group.id, member_id)
        # delete friendship relation.
        FriendshipService().delete(group.creator_id, member_id)
        return group

    def get_user_home_member(self, user_id):
        home = self.get_home(user_id)
        members = [uid for uid in home.members]
        return members

    def get_user_groups(self, user_id):
        member_records = GroupMemberService().get(member_id=user_id, deleted=False, many=True)

        groups = [str(record.group_id) for record in member_records]

        return groups

    def delete_person_relation(self, host_id, member_id):
        host_group = self.get_home(host_id)

        if host_group:
            self.delete_member(host_group, member_id)
            GroupMemberService().delete(group_id=host_group.id, member_id=member_id)

        member_group = self.get_home(member_id)

        if member_group:
            self.delete_member(member_group, member_id)
            GroupMemberService().delete(group_id=member_group.id, member_id=host_id)

        FriendshipService().delete(host_id, member_id)

        redis_tools.publish_delete_friend(member_id, host_id)

        return host_id, member_id


'''
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
'''


class GroupMemberService(BaseService):
    
    model = GroupMember
    serializer = GroupMemberSerializer
    
    def create(self, group, user_id, character, role):
        member = self.get(member_id=user_id, group_id=group.id)
        if not member:
            if character.endswith('s'):
                character = character[:-1]  # change members to member, admins to admin

            user = UserService().get(id=user_id)
            member = super(GroupMemberService, self).create(
                    member_id=user.id,
                    group_id=group.id,
                    authority=character,
                    group_remark_name=group.group_type,
                    nickname=user.nickname,
                    role=role
            )
        elif member.deleted:
            member.deleted = False
            member.save()

        return member

    def delete(self, group_id, member_id):
        record = self.get(group_id=group_id, member_id=member_id)
        super(GroupMemberService, self).delete(record)


class InvitationService(BaseService):

    model = Invitation
    serializer = InvitationSerializer

    def create(self, inviter_id, invitee_phone, group_id, role, append_msg):
        msg = {
            'invitee': invitee_phone,
            'role': role,
            'message': append_msg,
        }

        invitation = super(InvitationService, self).create(
            inviter=inviter_id,
            invitee=invitee_phone,
            group_id=group_id,
            role=role,
            message=msg)

        return invitation

    @transaction.atomic
    @api
    def accept(self, invitation_id):

        # add person to each other's group.
        invitation = self.get(id=invitation_id)
        invitee = UserService().get(phone=invitation.invitee)

        assert invitee is not None, 'invitee cannot be none'

        inviter_id = invitation.inviter
        invitee_id = invitee.id

        inviter_home = GroupService().get_home(invitation.inviter)
        GroupService().add_group_member(inviter_home, invitee_id, role=invitation.role)

        invitee_home = GroupService().get_home(invitee_id)
        reverse_role = roles.get_reverse_role(invitation.role, invitee.gender)

        GroupService().add_group_member(invitee_home, inviter_id, role=reverse_role)
        
        # update invitation.
        self.update(invitation, accepted=True, accept_time=datetime.now())

        # create friendship.
        FriendshipService().create(str(inviter_id), str(invitee_id))

        # publish redis message.
        redis_tools.accept_invitation(invitation, invitee_id)

        return invitation

    @api
    def reject(self, invitation_id):
        invitation = self.get(id=invitation_id)
        self.delete(invitation)
        return invitation

    @transaction.atomic
    @api
    def invite_person(self, inviter, group, invitee_phone, role, append_msg):
        invitation = self.create(inviter.id, invitee_phone, group.id, role, append_msg)
        invitee = UserService().get(phone=invitee_phone)
        if invitee:
            # if user is registered send to redis
            message = invitation.message
            redis_tools.publish_invitation(invitation, inviter, group, invitee, message)

        append_msg = str(append_msg).strip()

        succeed = MessageService.send_invitation(invitee_phone, inviter, append_msg, role)
        assert succeed, 'send invitation msg to {0} faild'.format(invitee_phone)

        return invitation


group_service = delegate(GroupService(), GroupService().serialize)
invitation_service = delegate(InvitationService(), InvitationService().serialize)
