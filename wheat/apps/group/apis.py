# -*- coding:utf-8 -*-

from rest_framework import permissions, viewsets, status
from rest_condition import Or

from customs.permissions import AllowPostPermission
from customs.response import SimpleResponse
from customs.viewsets import ListModelMixin
from apps.user.permissions import admin_required, login_required
from .services import GroupService
from .validators import check_request


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
                "name": "group name",
                "role": "p-grandfather/p-grandmother/m-grandfather/m-grandmother/father/mother/child"
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
        role = request.data.get('role')
        if not group_type or not name or not role:
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST)
        group = GroupService.create_group(request.user, group_type, name, role)
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
    def destroy(self, request, id):
        '''
        Delete group, requiring admin permission
        ---
        omit_serializer: true
        '''
        return SimpleResponse(status=status.HTTP_403_FORBIDDEN)


class InvitationViewSet(viewsets.GenericViewSet):

    """
    麦粒邀请相关API.
    ### Resource Description
    """
    model = GroupService._get_model('Invitation')
    queryset = model.get_queryset()
    serializer_class = GroupService.get_serializer('Invitation')
    lookup_field = 'id'
    permission_classes = [
        Or(permissions.IsAuthenticatedOrReadOnly, AllowPostPermission,)]

    @login_required
    def create(self, request):
        '''
        Invite user into group.
        ### Example Request

            {
                "group_id": "xxx",
                "invitee": "xxx",
                "role": "p-grandfather/p-grandmother/m-grandfather/m-grandmother/father/mother/child",
                "message": "xxx"
            }
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body
        '''
        group_id = request.data.get('group_id')
        invitee = request.data.get('invitee')
        role = request.data.get('role')
        message = request.data.get('message')
        if not group_id or not invitee or not role or not message:
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST)
        group = GroupService.get_group(id=group_id)
        if not group:
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST)
        invitation_dict = {
            'invitee': invitee,
            'role': role,
            'message': message
        }
        invitation = GroupService.create_group_invitation(group, request.user, invitation_dict)
        if invitation:
            return SimpleResponse(GroupService.serialize(invitation))
        return SimpleResponse(status=status.HTTP_400_BAD_REQUEST)

    @login_required
    @check_request('invitation')
    def update(self, request, id):
        '''
        Update invitation: accept invitation
        ### Example Request

            {
                "accepted": true/false
            }
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body
        '''
        accepted = request.data.get('accepted')
        if accepted is False:
            success = GroupService.delete_invitation(request.user, request.invitation)
            return SimpleResponse(success=success)
        elif accepted is True:
            success = GroupService.accept_invitation(request.user, request.invitation)
            return SimpleResponse(success=success)
        else:
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST)
