# -*- coding:utf-8 -*-

from django.http import Http404
from django.shortcuts import _get_queryset
from cacheops import invalidate_model


def get_or_none(klass, *args, **kwargs):
    objs = klass.objects.filter(*args, **kwargs)
    if len(objs) > 1 or len(objs) == 0:
        return None
    return objs[0]


def first_object_or_404(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    objs = queryset.filter(*args, **kwargs)
    if len(objs) > 0:
        return objs[0]
    else:
        raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)


def filter(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    objs = queryset.filter(*args, **kwargs)
    return objs


def cache_filter(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    objs = queryset.filter(*args, **kwargs)
    return objs


def invalidated_update(qs, **kwargs):
    n = qs.update(**kwargs)
    invalidate_model(qs.model)
    return n


def get_or_create(klass, defaults=None, **kwargs):
    queryset = _get_queryset(klass)
    objs = queryset.filter(**kwargs)
    if len(objs) > 0:
        return objs[0], False
    else:
        return queryset.get_or_create(defaults=defaults, **kwargs)
