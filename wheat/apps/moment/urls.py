# -*- coding:utf-8 -*-

from django.conf.urls import url, include
try:
    from collections import OrderedDict
except:
    from django.utils.datastructures import SortedDict as OrderedDict

import apis
from rest_framework.routers import DefaultRouter
from settings import API_VERSION

# Create a router and register our viewsets with it.
moment_router = DefaultRouter()
moment_router.register(r'moments', apis.MomentViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browseable API.
urlpatterns = []
urlpattern_dict = OrderedDict({
    'moment-api': url(r'^api/%s/' % API_VERSION,
                      include(moment_router.urls), name='moment-api'),

})

for name, urlpattern in urlpattern_dict.items():
    urlpatterns.append(urlpattern)
