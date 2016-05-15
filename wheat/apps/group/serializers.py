# -*- coding:utf-8 -*-

from customs.serializers import XModelSerializer
from customs.fields import DictStrField
from .models import Group, GroupMember, Invitation


class GroupSerializer(XModelSerializer):
    admins = DictStrField(required=False, allow_blank=True)
    members = DictStrField(required=False, allow_blank=True)
    #settings = DictStrField(required=False, allow_blank=True)

    class Meta:
        model = Group
        fields = ('id', 'group_type', 'name', 'creator_id',
                  'admins', 'members')


class GroupMemberSerializer(XModelSerializer):

    class Meta:
        model = GroupMember


class InvitationSerializer(XModelSerializer):

    class Meta:
        model = Invitation
