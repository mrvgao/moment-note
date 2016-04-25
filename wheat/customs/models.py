# -*- coding:utf-8 -*-

from json import JSONEncoder

from django.db.models.fields.related import ForeignKey
from django.db import models
from django.http import Http404
from django.db.models.query import QuerySet
from django.conf import settings

import logging
logger = logging.getLogger('query')


def query2str(*args, **kwargs):
    qs = {}
    for i, q in enumerate(args):
        qs['_Q_%d' % i] = str(q)
    for k, v in kwargs.items():
        if isinstance(v, models.Model):
            qs['%s_id' % k] = v.pk
        else:
            qs[k] = v
    return JSONEncoder().encode(qs)


class CommonUpdateAble(models.Model):

    def update(self, **kwargs):
        _delete_null_params(kwargs)
        fields = {}
        changed = False
        for f in self._meta.fields:
            fields[f.name] = f
        for k, v in kwargs.items():
            if k in fields:
                if getattr(self, k) != v:
                    setattr(self, k, v)
                    changed = True
            elif k.endswith('_id'):
                f = fields.get(k.rsplit('_', 1)[0])
                if f is not None and type(f) is ForeignKey:
                    if getattr(self, k) != v:
                        setattr(self, k, v)
                        changed = True
        if changed:
            self.save()
        return self

    class Meta:
        abstract = True


class CacheableQuerySet(QuerySet):

    def is_cacheable(self):
        if settings.CACHE_QUERY:
            return getattr(self.model, 'CACHEABLE', True)
        return False

    def update(self, **kwargs):
        # TODO: not sure whether should invalidate first or update first
        # from cacheops import invalidate_obj
        # for obj in self.iterator():
        #    invalidate_obj(obj)
        # update must behind invalidate obj
        _delete_null_params(kwargs)
        n = super(CacheableQuerySet, self).update(**kwargs)
        if self.is_cacheable():
            from cacheops import invalidate_model
            invalidate_model(self.model)
        return n


def _delete_null_params(params):
    keys = filter(lambda k: params[k] == settings.NULL, params.keys())
    map(lambda k: params.pop(k, None), keys)


class CacheableManager(models.Manager):

    def get_queryset(self):
        if getattr(self, 'queryset', None) is None:
            return CacheableQuerySet(self.model, using=self._db)
        else:
            return self.queryset

    def get_cache_timeout(self):
        return getattr(self.model, 'CACHE_TIMEOUT', settings.DEFAULT_CACHE_TIMEOUT)

    def is_cacheable(self):
        if settings.CACHE_QUERY:
            return getattr(self.model, 'CACHEABLE', True)
        return False

    def all(self):
        queryset = self.get_queryset()
        if self.is_cacheable():
            objs = queryset.all().cache(timeout=self.get_cache_timeout())
        else:
            objs = queryset.all()
        return objs

    def filter(self, *args, **kwargs):
        _delete_null_params(kwargs)
        queryset = self.get_queryset()
        if self.is_cacheable():
            objs = queryset.filter(*args, **kwargs).cache(timeout=self.get_cache_timeout())
        else:
            objs = queryset.filter(*args, **kwargs)
        return objs

    def query(self, *args, **kwargs):
        _delete_null_params(kwargs)
        order_by = kwargs.pop('_order_by', None)
        page = kwargs.pop('_page', None)
        last_limit = kwargs.pop('_last_limit', None)
        objs = self.filter(*args, **kwargs)
        if order_by:
            objs = objs.order_by(order_by)
        if page:
            begin_i = settings.PAGE_SIZE * (int(page) - 1)
            end_i = begin_i + settings.PAGE_SIZE
            return objs[begin_i:end_i]
        elif last_limit:
            return objs.reverse()[:int(last_limit):-1]
        return objs

    def find(self, *args, **kwargs):
        _delete_null_params(kwargs)
        queryset = self.get_queryset()
        objs = queryset.filter(*args, **kwargs)
        return objs

    def get(self, *args, **kwargs):
        # queryset = super(CacheableManager, self).get_queryset()
        _delete_null_params(kwargs)
        queryset = self.get_queryset()
        if self.is_cacheable():
            objs = queryset.filter(*args, **kwargs).cache(timeout=self.get_cache_timeout())
        else:
            objs = queryset.filter(*args, **kwargs)
        if not objs:
            return self.this(*args, **kwargs)
        elif len(objs) > 1:
            logger.error('%s: %s' % ("get() returned more than one %s -- it returned %s!" %
                                     (queryset.model._meta.object_name, objs.count()), query2str(*args, **kwargs)))
            raise queryset.model.MultipleObjectsReturned(
                "get() returned more than one %s -- it returned %s!" % (
                    queryset.model._meta.object_name, objs.count()))
        else:
            return objs[0]

    def get_or_404(self, *args, **kwargs):
        _delete_null_params(kwargs)
        queryset = self.get_queryset()
        if self.is_cacheable():
            objs = queryset.filter(*args, **kwargs).cache(timeout=self.get_cache_timeout())
        else:
            objs = queryset.filter(*args, **kwargs)
        if not objs:
            raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)
        elif len(objs) > 1:
            logger.error('%s: %s' % ("get() returned more than one %s -- it returned %s!" %
                                     (queryset.model._meta.object_name, objs.count()), query2str(*args, **kwargs)))
            raise queryset.model.MultipleObjectsReturned(
                "get() returned more than one %s -- it returned %s!" % (
                    queryset.model._meta.object_name, objs.count()))
        else:
            return objs[0]

    def get_or_none(self, *args, **kwargs):
        _delete_null_params(kwargs)
        try:
            obj = self.get(*args, **kwargs)
            return obj
        except Exception as e:
            logger.error(e)
            return None

    def this(self, *args, **kwargs):
        # queryset = super(CacheableManager, self).get_queryset()
        _delete_null_params(kwargs)
        queryset = self.get_queryset()
        objs = queryset.filter(*args, **kwargs)
        if not objs:
            logger.error('%s: %s' % ("%s matching query does not exist." %
                                     queryset.model._meta.object_name, query2str(*args, **kwargs)))
            raise queryset.model.DoesNotExist("%s matching query does not exist." % queryset.model._meta.object_name)
        elif len(objs) > 1:
            logger.error('%s: %s' % ("this() returned more than one %s -- it returned %s!" %
                                     (queryset.model._meta.object_name, objs.count()), query2str(*args, **kwargs)))
            raise queryset.model.MultipleObjectsReturned(
                "this() returned more than one %s -- it returned %s!" % (
                    queryset.model._meta.object_name, objs.count()))
        else:
            return objs[0]

    def update_or_create(self, defaults=None, **kwargs):
        _delete_null_params(kwargs)
        try:
            obj = self.get(**kwargs)
            if defaults:
                obj.update(**defaults)
            return obj, False
        except Exception as e:
            logger.error(e)
            if defaults:
                kwargs.update(defaults)
            obj = self.create(**kwargs)
            return obj, True

    def defer(self, *args, **kwargs):
        _delete_null_params(kwargs)
        cm = CacheableManager()
        cm.queryset = self.get_queryset().defer(*args, **kwargs)
        return cm

    def only(self, *args, **kwargs):
        _delete_null_params(kwargs)
        cm = CacheableManager()
        cm.queryset = self.get_queryset().only(*args, **kwargs)
        return cm


class JSONDictModel(object):

    def __init__(self, **kwargs):
        self.data = kwargs


class EnhancedModel(object):

    @classmethod
    def get_queryset(cls):
        return cls.objects.all()
