from django.conf.urls import url, include
from settings import API_VERSION
from rest_framework.routers import DefaultRouter


def get_urlpattern(views, api_name):
    '''
    Create url by views and url_name, add prefix to url.
    ### Example:

    get_url(views={'user': viewset_1, 'user-new': viewset_2})

    System will get the pages /api/0.1/user, /api/0.1/user_2
    '''
    router = DefaultRouter()
    for name, view in views.items():
        router.register(r'%s' % name, view)

    urlpatterns = [
        url(r'^api/%s/' % API_VERSION, include(router.urls), name=api_name)
    ]

    return urlpatterns


def get_url(api_name, resource):
    return '/api/%s/%s%s' % (str(API_VERSION), api_name, resource)
