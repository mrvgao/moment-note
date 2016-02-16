# -*- coding:utf-8 -*-

from datetime import datetime
from django.db import transaction

from customs.services import BaseService
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
