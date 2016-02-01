# -*- coding:utf-8 -*-

from collections import OrderedDict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins

# from apps.user.permissions import admin_required


def get_urls(urllist, prefix='^'):
    urls = []
    for entry in urllist:
        urls.append(prefix + entry.regex.pattern[1:])
        if hasattr(entry, 'url_patterns'):
            urls += get_urls(entry.url_patterns, prefix + entry.regex.pattern[1:])
    return urls


class ObjListSerializerMixin(object):

    def serialize_objs(self, obj_list, serializer_cls, request=None):
        data = []
        for obj in obj_list:
            if request is None:
                data.append(OrderedDict(serializer_cls(obj).data))
            else:
                data.append(OrderedDict(serializer_cls(obj, context={'request': request}).data))
        return data


class ListUrls(APIView):

    # @admin_required
    def get(self, request, format=None):
        """
        Return a list of all urls.
        """
        import urls
        url_list = get_urls(urls.urlpatterns)
        url_set = set(url_list)
        url_list = list(url_set)
        url_list.sort()
        return Response(url_list)


class UpdateModelMixin(object):

    """
    Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class ListModelMixin(mixins.ListModelMixin):

    def list(self, request, *args, **kwargs):
        response = super(ListModelMixin, self).list(request, *args, **kwargs)
        return Response(response.data['results'])
