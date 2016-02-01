# -*- coding:utf-8 -*

from collections import OrderedDict
from json import JSONDecoder
from django.conf import settings
from rest_framework import serializers


class ListStrField(serializers.CharField):

    def to_representation(self, obj):
        if isinstance(obj, list):
            return obj
        return JSONDecoder().decode(obj if obj else '[]')


class DictStrField(serializers.CharField):

    def to_representation(self, obj):
        if isinstance(obj, dict):
            return obj
        return JSONDecoder().decode(obj if obj else '{}')


class OrderedDictStrField(serializers.CharField):

    def to_representation(self, obj):
        if isinstance(obj, dict):
            return obj
        return JSONDecoder(object_pairs_hook=OrderedDict).decode(obj if obj else '{}')


class FakeIntegerField(serializers.IntegerField):

    def get_attribute(self, instance):
        """
        Given the *outgoing* object instance, return the primitive value
        that should be used for this field.
        """
        return 0


class FakeBooleanField(serializers.BooleanField):

    def get_attribute(self, instance):
        """
        Given the *outgoing* object instance, return the primitive value
        that should be used for this field.
        """
        return False


class FakeCharField(serializers.CharField):

    def get_attribute(self, instance):
        """
        Given the *outgoing* object instance, return the primitive value
        that should be used for this field.
        """
        return ''


class XImageField(serializers.ImageField):

    def to_representation(self, obj):
        if str(obj).startswith('http'):
            return str(obj)
        elif str(obj) != '':
            return '%s%s%s' % (settings.BASE_URL, settings.MEDIA_URL, str(obj))
        else:
            return ''
