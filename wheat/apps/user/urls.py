# -*- coding:utf-8 -*-

from customs.urls import get_urlpattern
import apis

urlpatterns = get_urlpattern({
    'user': apis.UserViewSet,
    'new-user': apis.UserViewSet,
}, api_name='user-api')
