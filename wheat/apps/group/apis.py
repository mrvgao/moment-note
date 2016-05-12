# -*- coding:utf-8 -*-

from rest_framework import permissions, viewsets, status
from rest_condition import Or

from customs.permissions import AllowPostPermission
from customs.response import SimpleResponse
from customs.viewsets import ListModelMixin
from apps.user.permissions import admin_required, login_required
from .services import group_service
from .services import invitation_service
from apps.user.services import UserService
from .validators import check_request
from errors import codes
from . import services
from rest_framework.decorators import detail_route
from customs import class_tools
from customs import request_tools


@class_tools.set_service(invitation_service)
class InvitationViewSet(viewsets.GenericViewSet):

    """
    麦粒邀请相关API.
    ### Resource Description
    """
    INVITATION = 'Invitation'

    @login_required
    @request_tools.post_data_check(['group_id', 'invitee', 'role', 'message'])
    def create(self, request):
        '''
        Invite user into group.
        该接口所需的group_id 请在/api/0.1/users/{id}/home 进行获取

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

        GROUP_ID, INVITEE = 'group_id', 'invitee'
        ROLE, MESSAGE = 'role', 'message'

        group_id = request.data.get(GROUP_ID)
        invitee = request.data.get(INVITEE)
        role = request.data.get(ROLE)
        message = request.data.get(MESSAGE)

        group = invitation_service.get(id=group_id)

        if not group:
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST, errors="this group not found")
        elif str(invitee) == str(request.user.phone):
            return SimpleResponse(status=403, errors='cannot invitee your self')

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
                raise SyntaxError('role should be valid and invitee and message cannot be null')
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
