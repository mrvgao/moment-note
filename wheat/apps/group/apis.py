# -*- coding:utf-8 -*-

from rest_framework import permissions, viewsets, status
from rest_condition import Or

from customs.permissions import AllowPostPermission
from customs.response import SimpleResponse
from customs.viewsets import ListModelMixin
from apps.user.permissions import login_required
from .services import GroupService
from apps.user.services import UserService
from .validators import check_request
from errors import codes
from . import services
from rest_framework.decorators import list_route


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
                result = GroupService.get_or_create_group(
                    owner_id,
                    ALL_FRIENDS
                )
            elif group_type is None:
                result = GroupService.filter_group(creator_id=owner_id)
            else:
                result = GroupService.filter_group(creator_id=owner_id, group_type=group_type)

            GroupViewSet._get_group_member_info(result)
            result = GroupService.serialize_list(result)
            return SimpleResponse(result)
        else:
            response = super(GroupViewSet, self).list(request)
            return SimpleResponse(response.data)

    @staticmethod
    def _get_group_member_info(groups):
        GroupService.add_member_avatar_of_groups(groups)
        GroupService.add_member_activity_of_groups(groups)

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
                "role": "f-grandfather/f-grandmother/m-grandfather/m-grandmother/father/mother/child"
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
        GroupService.add_member_avatar_of_group(group)
        GroupService.add_member_activity_of_group(group)
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

        NAME = 'name'
        name = request.data.get(NAME)
        if name:
            group.update(name=name)
            return SimpleResponse(GroupService.serialize(group))
        return SimpleResponse(status=status.HTTP_400_BAD_REQUEST)


class FriendViewSet(ListModelMixin, viewsets.GenericViewSet):
    """
    Friend View
    ### Resource Description
    """
    model = GroupService._get_model()
    queryset = model.get_queryset()
    serializer_class = GroupService.get_serializer()
    lookup_field = 'id'
    permission_classes = [
        Or(permissions.IsAuthenticatedOrReadOnly, AllowPostPermission,)]

    def list(self, request):
        pass

    def create(self, request):
        pass

    def update(self, request, id):
        pass

    def retrieve(self, request, id):
        pass

    @login_required
    def destroy(self, request, id):
        '''
        Delete person which uid is *id* from requset.user's home group.
        ---
        omit_serializer: true
        '''
        try:
            GroupService.delete_person_from_each_group(
                host_id=request.user.id, member_id=id)
            return SimpleResponse(success=True)
        except Exception as e:
            return SimpleResponse(
                status=status.HTTP_403_FORBIDDEN,
                errors=e.message
            )


class InvitationViewSet(viewsets.GenericViewSet):

    """
    麦粒邀请相关API.
    ### Resource Description
    """
    INVITATION = 'Invitation'
    model = GroupService._get_model()
    queryset = model.get_queryset()
    serializer_class = GroupService.get_serializer(INVITATION)
    lookup_field = 'id'
    permission_classes = [
        Or(permissions.IsAuthenticatedOrReadOnly, AllowPostPermission,)]

    @login_required
    def create(self, request):
        '''
        Invite user into group.
        该接口所需的group_id 请在/api/0.1/groups/ 将type设置为all_home_member进行获取
        !注意: 测试该接口前 请先登录

        ### 目前支持的关系：
            {
                'm-grandfather': u'外公',
                'm-grandmother': u'外婆',
                'f-grandfather': u'爷爷',
                'f-grandmother': u'奶奶',
                'father': u'爸爸',
                'mother': u'妈妈',
                'child': u'孩子',
                'wife': u'老婆',
                'husband': u'老公',
                'son': u'儿子',
                'daughter': u'女儿',
                'slibe':u'哥哥/弟弟',
                'sister':u'姐姐／妹妹',
                'l-father': '公公',
                'l-mother': '婆婆',
                'suocero': '岳父',
                'suocera': '岳母',
                'qj-g': '亲家母',
                'qj-m': '亲家公',
                'l-son': '女婿'
            }

        ### Example Request

            {
                "group_id": "a2b7c193f5df42a69942d0bc848c0467",
                "invitee": "18805710001",
                "role": "p-grandfather/p-grandmother/...",
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

        GROUP_ID, INVITEE, ROLE, MESSAGE = 'group_id', 'invitee', 'role', 'message'
        group_id = request.data.get(GROUP_ID)
        invitee = request.data.get(INVITEE)
        role = request.data.get(ROLE)
        message = request.data.get(MESSAGE)
        if not group_id or not invitee or not role or not message:
            return SimpleResponse(
                status=status.HTTP_400_BAD_REQUEST,
                errors='role should be valid and invitee and message cannot be null')

        code = GroupService.check_if_valid_invitation(request.user, invitee, role)
        if code != codes.OK:
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST, errors=codes.errors(code))

        group = GroupService.get_group(id=group_id)
        if not group or group.creator_id != str(request.user.id):
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST, errors="this group not found")
        elif invitee == request.user.phone:
            return SimpleResponse(status=status.HTTP_403_FORBIDDEN, errors='cannot invitee your self')

        invitation_dict = {
            INVITEE: invitee,
            ROLE: role,
            MESSAGE: message
        }
        user_id = request.user.id
        try:
            return self._create_invitation_by_group_and_user_id(user_id, group, invitation_dict)
        except SyntaxError as e:
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST, errors=e.message)
        except ReferenceError as e:
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST, errors=e.message)

    def _create_invitation_by_group_and_user_id(self, user_id, group, invitation_dict):
        '''
        Creates invitation message by group and user_id

        Raises:
            SyntaxError: if invitation initial informaiton is error, e.g,
            wrong user, wrong group, wrong dict, will raise this error
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
                raise SyntaxError('role should be valid and invitee and message cannot be null')
        else:
            raise ReferenceError('user id is error, no this user')  # not login

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

        ### Response:

        + 403 : this role is duplicate in target person's group.
        + 406 : role is unacceptable
        + 409 : this person is alreay in target person's group
        + 413 : group member overflowed.
        + {success: true}

        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body
        '''
        ACCEPTED = 'accepted'
        accepted = request.data.get(ACCEPTED, False)

        user_id = request.user.id

        if user_id:
            invitee = UserService.get_user(id=user_id)

        success = True
        if accepted is False:
            success = GroupService.delete_invitation(
                invitee,
                request.invitation
            )
        else:
            try:
                GroupService.accept_group_invitation(invitee, request.invitation)
            except NameError as e:
                return SimpleResponse(
                    status=406,
                    errors='role ' + e.message + ' unacceptable'
                )
            except ReferenceError as e:
                return SimpleResponse(
                    status=409,
                    errors=e.message + ' already in target person group'
                )
            except IndexError:
                return SimpleResponse(
                    status=413,
                    errors='group member number overflow'
                )
            except KeyError as e:
                return SimpleResponse(
                    status=403,
                    errors=e.message + ' already in target person group'
                )
            except Exception as e:
                return SimpleResponse(
                    status=status.HTTP_400_BAD_REQUEST,
                    errors=e.message
                )

        return SimpleResponse(success=success)

    @list_route(methods=['get'])
    def check(self, request):
        '''
        检查邀请是否valid

        inviter -- inviter's id
        invitee -- invitee's phone
        role -- invitee's role for inviter
        ---
        omit_serializer: true
        '''
        inviter_id = request.query_params.get('inviter')
        invitee_phone = request.query_params.get('invitee')
        role = request.query_params.get('role')
        inviter = UserService.get_user(id=inviter_id)
        if not inviter:
            return SimpleResponse(status=status.HTTP_404_NOT_FOUND, errors='no this inviter')
        code = GroupService.check_if_valid_invitation(inviter, invitee_phone, role)
        if code != codes.OK:
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST, errors=codes.errors(code))
        return SimpleResponse(success=True)
