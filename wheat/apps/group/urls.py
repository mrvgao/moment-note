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
group_router = DefaultRouter()
group_router.register(r'groups', apis.GroupViewSet)

invitation_router = DefaultRouter()
invitation_router.register(r'invitations', apis.InvitationViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browseable API.
urlpatterns = []
urlpattern_dict = OrderedDict({
    'group-api': url(r'^api/%s/' % API_VERSION,
                     include(group_router.urls), name='group-api'),
    'invitation-api': url(r'^api/%s/' % API_VERSION,
                          include(invitation_router.urls), name='invitation-api'),

})

for name, urlpattern in urlpattern_dict.items():
    urlpatterns.append(urlpattern)
