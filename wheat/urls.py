# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

# from weixin.weixin import check_signature, auth
urlpatterns = patterns(
    '',
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# add api urls here
try:
    urlpatterns += [
        url(r'^api/%s/auth/' % settings.API_VERSION,
            include('rest_framework.urls', namespace='rest_framework')),
        url(r'^docs/', include('rest_framework_swagger.urls', namespace='rest_framework_swagger')),

        url(r'^', include('apps.user.urls')),  # Don't set namespace
        url(r'^', include('apps.group.urls')),  # Don't set namespace
        url(r'^', include('apps.moment.urls')),  # Don't set namespace
        url(r'^', include('apps.image.urls')),  # Don't set namespace
        url(r'^', include('apps.book.urls')),  # Don't set namespace
        url(r'^', include('apps.order.urls')),  # Don't set namespace
    ]
except Exception as e:
    print e
