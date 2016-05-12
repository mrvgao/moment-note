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
from customs.response import APIResponse


@class_tools.set_service(invitation_service)
class InvitationViewSet(viewsets.GenericViewSet):

    """
    麦粒邀请相关API.
    ### Resource Description
    """

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
        
        group = invitation_service.get(request.data.get('group_id', None))
        invitee_phone = request.data('invitee', None)
        role = request.data.get('role', None)
        message = request.data.get('message', None)
        
        error, status_code = None, status.HTTP_200_OK

        if not group_service.consist_member(group.id, id=self.user.id):
            error, status_code = codes.GROUP_NOT_EXIST, status.HTTP_403_FORBIDDEN
        elif group_service.consist_member(group.id, phone=invitee_phone):
            error, status_code = codes.USER_ALRAEDY_EXIST, status.HTTP_409_CONFLICT
        elif not group_service.role_is_valid(role):
            error, status_code = codes.ROLE_INVALID, status.HTTP_406_NOT_ACCEPTABLE

        invitation = None
        
        if not error:
            invitation = group_service.invite_person(request.user, group, invitee_phone, role, message)

        result = error or invitation  # if error is not none, return error

        return APIResponse(result, status=status_code)

    @login_required
    @check_request('invitation')
    @request_tools.post_data_check(['accepted'])
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

        + {success: true}

        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body
        '''

        accept = request.data.get('accept', False)

        invitation_id = id

        if accept:
            invitation = invitation_service.accept(invitation_id)
        else:
            invitation = invitation_service.reject(invitation_id)

        return SimpleResponse(invitation)
