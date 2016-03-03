# -*- coding:utf-8 -*-

from rest_framework import permissions, viewsets, status
from rest_condition import Or

from customs.permissions import AllowPostPermission
from customs.response import SimpleResponse
from customs.viewsets import ListModelMixin
from apps.user.permissions import admin_required, login_required
from .services import GroupService
from apps.user.services import UserService
from .validators import check_request
from errors import codes


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

    # @admin_required
    @login_required
    def list(self, request):
        '''
        获得群组的列表，若owner-id和type为空 则列出全部群组的id
        在邀请好友时候，系统需要一个group_id，该group承载该用户的所有好友
        要获得该group_id，需要将type设置为all_home_member

        List all groups by pages. Admin Required.

        page -- page
        owner-id -- group所有者的id
        type -- 该group的类型， 邀请好友请设置为all_home_member
        ---
        omit_serializer: true
        '''

        OWNER_ID = 'owner-id'
        TYPE = 'type'
        owner_id = request.query_params.get(OWNER_ID, None)
        group_type = request.query_params.get(TYPE, None)

        ALL_FRIENDS = 'all_home_member'

        if owner_id:
            if group_type == ALL_FRIENDS:
                result = GroupService.get_group_if_without_create(
                    owner_id,
                    ALL_FRIENDS
                )
            elif group_type is None:
                result = GroupService.filter_group(creator_id=owner_id)
            else:
                result = GroupService.filter_group(creator_id=owner_id, group_type=group_type)

            result = GroupService.serialize_list(result)
            return SimpleResponse(result)
        else:
            response = super(GroupViewSet, self).list(request)
            return SimpleResponse(response.data)

    def _get_specific_group(owner_id, group_type):
        '''
        Gets specific group's information by owner_id and group_type.
        Returns:
            this group list.

        '''
        pass

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
        该接口所需的group_id 请在/api/0.1/groups/ 将type设置为all_home_member进行获取
        !注意: 测试该接口前 请先登录
        ### Example Request

            {
                "group_id": "a2b7c193f5df42a69942d0bc848c0467",
                "invitee": "18805710001",
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
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST, errors="this group not found")

        invitation_dict = {
            'invitee': invitee,
            'role': role,
            'message': message
        }

        user_id = request.session.get('user_id', None)

        user_okay = False
        invitation_okay = False

        try:
            request
            return self._create_invitation_by_group_and_user_id(user_id, group, invitation_dict)
        except SyntaxError as e:
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST, errors="invitation is unvalid")
        except ReferenceError as e:
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST, errors="You haven't login before giving invitation")

    def _create_invitation_by_group_and_user_id(self, user_id, group, invitation_dict):
        '''
        Creates invitation message by group and user_id

        Raises:
            SyntaxError: if invitation initial informaiton is error, e.g, wrong user, wrong group, wrong dict, will raise this error
            ReferenceError: if give wrong user_id, raise this error

        Returns:
            SimpleResponse: Invitation Response

        Author: Minchiuan 2016-2-23
        '''

        user = UserService.get_user(id=user_id)
        if user:
            invitation = GroupService.create_group_invitation(group, user, invitation_dict)
            if invitation:
                return SimpleResponse(GroupService.serialize(invitation))
            else:
                raise SyntaxError('invitation initial message is error')
        else:
            raise ReferenceError('user id is error, no this user') # not login

    @login_required
    @check_request('invitation')
    def update(self, request, id):
        '''
        Update invitation: accept invitation
        !注意: 测试该接口前 请先登录

        args:
            id: 某个邀请信息的id

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

        user_id = request.session.get('user_id', None)

        if user_id:
            user = UserService.get_user(id=user_id)

        if user is None:
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST, erros=codes.LOGIN_REQUIRED_MSG)
        if accepted is False:
            success = GroupService.delete_invitation(user, request.invitation)
            return SimpleResponse(success=success)
        elif accepted is True:
            success = GroupService.accept_group_invitation(user, request.invitation)
            if success:
                return SimpleResponse(success=success)
            else:
                return SimpleResponse(success=False, errors=codes.LOGIN_REQUIRED_MSG)
        else:
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST)
