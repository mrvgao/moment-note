# -*- coding:utf-8 -*-

from customs.serializers import XModelSerializer
from customs.fields import XImageField, DictStrField
from .models import Group, GroupMember, Invitation


class GroupSerializer(XModelSerializer):
    avatar = XImageField(
        max_length=100,
        allow_empty_file=False,
        required=False,
        use_url=True,
        style={'input_type': 'file'})
    admins = DictStrField(required=False, allow_blank=True)
    members = DictStrField(required=False, allow_blank=True)
    settings = DictStrField(required=False, allow_blank=True)

    class Meta:
        model = Group
        fields = ('id', 'group_type', 'name',
                  'avatar', 'creator_id',
                  'admins', 'members', 'max_members',
                  'settings', 'created_at', 'updated_at')


class GroupMemberSerializer(XModelSerializer):

    class Meta:
        model = GroupMember


class InvitationSerializer(XModelSerializer):

    class Meta:
        model = Invitation
