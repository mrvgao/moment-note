# -*- coding:utf-8 -*-

from datetime import datetime
from django.db import transaction

from customs.services import BaseService
from .models import Group, GroupMember
from .serializers import GroupSerializer, GroupMemberSerializer


class GroupService(BaseService):

    @classmethod
    def _get_model(cls, name='Group'):
        if name == 'Group':
            return Group
        elif name == 'GroupMember':
            return GroupMember

    @classmethod
    def get_serializer(cls, model='Group'):
        if model == 'Group':
            return GroupSerializer
        elif model == 'GroupMember':
            return GroupMemberSerializer

    @classmethod
    def serialize(cls, obj, context={}):
        if isinstance(obj, Group):
            return GroupSerializer(obj, context=context).data
        elif isinstance(obj, GroupMember):
            return GroupMemberSerializer(obj, context=context).data

    @classmethod
    def get_group(cls, **kwargs):
        return Group.objects.get_or_none(**kwargs)

    @classmethod
    @transaction.atomic
    def create_group(cls, creator, group_type, name):
        if not Group.valid_group_type(group_type):
            return None
        # 每个人只能创建一个小家
        if group_type == 'family':
            group = Group.objects.get_or_none(
                creator_id=creator.id,
                group_type=group_type)
            if group:
                return group
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
                'joined_at': datetime.now()
            }})
        GroupMember.objects.create(
            member_id=creator.id,
            group_id=group.id,
            authority='admin',
            group_remark_name=name,
            avatar=creator.avatar)
        return group

    @classmethod
    @transaction.atomic
    def add_group_member(cls, group, user):
        if user.id not in group.members:
            group.members[user.id] = {
                'name': user.nickname,
                'joined_at': datetime.now()
            }
            group.save()
            GroupMember.objects.create(
                member_id=user.id,
                group_id=group.id,
                group_remark_name=group.name,
                avatar=user.avatar)
            return True
        return False
