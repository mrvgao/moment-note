# -*- coding:utf-8 -*-

from datetime import datetime
from django.db import transaction
from django.db.models import Q

from customs.services import BaseService
from apps.user.services import UserService
from apps.group.services import GroupService
from .models import Moment
from .serializers import MomentSerializer


class MomentService(BaseService):

    @classmethod
    def _get_model(cls, name='Moment'):
        if name == 'Moment':
            return Moment

    @classmethod
    def get_serializer(cls, model='Moment'):
        if model == 'Moment':
            return MomentSerializer

    @classmethod
    def serialize(cls, obj, context={}):
        if isinstance(obj, Moment):
            return MomentSerializer(obj, context=context).data

    @classmethod
    def get_moment(cls, **kwargs):
        return Moment.objects.get_or_none(**kwargs)

    @classmethod
    def get_moments(cls, **kwargs):
        return Moment.objects.filter(**kwargs)

    @classmethod
    @transaction.atomic
    def create_moment(cls, **kwargs):
        user_id = kwargs.get('user_id')
        content_type = kwargs.get('content_type')
        content = kwargs.get('content')
        moment_date = kwargs.get('moment_date', datetime.now())
        visible = kwargs.get('visible')
        if user_id and Moment.valid_content_type(content_type, content) \
                and Moment.valid_visible_field(visible):
            moment = Moment.objects.create(
                user_id=user_id,
                content_type=content_type,
                content=content,
                moment_date=moment_date,
                visible=visible)
            return moment
        return None

    @classmethod
    @transaction.atomic
    def delete_moment(cls, moment):
        if not moment.deleted:
            moment.deleted = True
            moment.save()
        return True

    @classmethod
    def get_user_moments(cls, user_id):
        friend_ids = UserService.get_user_friend_ids(user_id)
        group_ids = GroupService.get_user_group_ids(user_id)
        moments = Moment.objects.filter(
            Q(Q(user_id__in=friend_ids) & Q(visible__in=['public', 'friends'])) |
            Q(visible__in=group_ids) |
            Q(user_id=user_id),
            deleted=False).order_by('post_date')
        return moments

    @classmethod
    def get_moments_from_user(cls, user_id):
        moments = Moment.objects.filter(
            user_id=user_id,
            deleted=False).order_by('post_date')
        return moments
