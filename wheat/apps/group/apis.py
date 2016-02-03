# -*- coding:utf-8 -*-

from rest_framework import permissions, viewsets, status
from rest_condition import Or

from customs.permissions import AllowPostPermission
from customs.response import SimpleResponse
from customs.viewsets import ListModelMixin
from apps.user.permissions import admin_required, login_required
from .services import GroupService


class GroupViewSet(ListModelMixin,
                   viewsets.GenericViewSet):

    """
    麦粒群组系统相关API.
    ### Resource Description
    """
    model = GroupService._get_model()
    queryset = model.get_queryset()
    serializer_class = GroupService.get_serializer()
    lookup_field = 'id'
    permission_classes = [
        Or(permissions.IsAuthenticatedOrReadOnly, AllowPostPermission,)]

    @admin_required
    def list(self, request):
        '''
        List all groups by pages. Admin Required.
        page -- page
        ---
        omit_serializer: true
        '''
        response = super(GroupViewSet, self).list(request)
        return SimpleResponse(response.data)

    @login_required
    def create(self, request):
        '''
        Create Group.
        ### Request Example

            {
                "group_type": "common/family",
                "name": "group name"
            }
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body
        '''
        group_type = request.data.get('group_type')
        name = request.data.get('name')
        if not group_type or not name:
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST)
        group = GroupService.create_group(request.user, group_type, name)
        if group:
            return SimpleResponse(GroupService.serialize(group))
        return SimpleResponse(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, id):
        '''
        Retrieve Group info.
        ---
        omit_serializer: true
        '''
        group = GroupService.get_group(id=id)
        if not group:
            return SimpleResponse(status=status.HTTP_404_NOT_FOUND)
        return SimpleResponse(GroupService.serialize(group))

    def update(self, request, id):
        '''
        Update group.
        ### Example Request

            {
                "name": "new group name"
            }
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body
        '''
        group = GroupService.get_group(id=id)
        if not group:
            return SimpleResponse(status=status.HTTP_404_NOT_FOUND)
        name = request.data.get('name')
        if name:
            group.update(name=name)
            return SimpleResponse(GroupService.serialize(group))
        return SimpleResponse(status=status.HTTP_400_BAD_REQUEST)

    @admin_required
    def destroy(self, request, id, *args, **kwargs):
        '''
        Delete group, requiring admin permission
        ---
        omit_serializer: true
        '''
        return SimpleResponse(status=status.HTTP_403_FORBIDDEN)
