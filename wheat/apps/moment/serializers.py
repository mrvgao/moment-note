# -*- coding:utf-8 -*-

from customs.serializers import XModelSerializer
from customs.fields import DictStrField
from .models import Moment


class MomentSerializer(XModelSerializer):
    content = DictStrField(required=False, allow_blank=True)

    class Meta:
        model = Moment
        fields = ('id', 'user_id', 'content_type', 'content',
                  'post_date', 'moment_date', 'visible', 'deleted', 'tags')
