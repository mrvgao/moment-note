# -*- coding:utf-8 -*-

from rest_framework import serializers

from .models import JSONDictModel


def clean_data(dict_obj, fields):
    for field, val in dict_obj.items():
        if field not in fields:
            dict_obj.pop(field, None)
    return dict_obj


class XModelSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        if isinstance(instance, self.Meta.model):
            data = super(XModelSerializer, self).to_representation(instance)
            if hasattr(self.Meta, 'represent_fields'):
                clean_data(data, self.Meta.represent_fields)
            return data
        elif isinstance(instance, JSONDictModel):
            return instance.data
        else:
            return instance
