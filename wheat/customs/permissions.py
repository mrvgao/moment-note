# -*- coding:utf-8 -*-

import os

from rest_framework import permissions

env = os.environ.get("DJANGO_CONFIGURATION", "Production")


def conditional_permission_classes(default_cls):
    if env == 'Local':
        return (permissions.AllowAny,)
    return default_cls


class AllowPostPermission(permissions.BasePermission):

    """
    Allow Post Method
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return False
