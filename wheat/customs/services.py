# -*- coding:utf-8 -*-

from collections import OrderedDict


class BaseService:

    @classmethod
    def serialize_objs(cls, obj_list, request=None):
        data = []
        for obj in obj_list:
            if request is None:
                data.append(OrderedDict(cls.serialize(obj)))
            else:
                data.append(OrderedDict(cls.serialize(obj, context={'request': request})))
        return data
