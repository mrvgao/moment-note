# -*- coding:utf-8 -*-

from rest_framework import permissions, viewsets, status
from rest_condition import Or

from customs.permissions import AllowPostPermission
from customs.response import SimpleResponse
from customs.viewsets import ListModelMixin
from apps.user.permissions import admin_required, login_required
from .services import MomentService


class MomentViewSet(ListModelMixin,
                    viewsets.GenericViewSet):

    """
    麦粒和家系统相关API.
    ### Resource Description
    """
    model = MomentService._get_model()
    queryset = model.get_queryset()
    serializer_class = MomentService.get_serializer()
    lookup_field = 'id'
    permission_classes = [
        Or(permissions.IsAuthenticatedOrReadOnly, AllowPostPermission,)]

    @admin_required
    def list(self, request):
        '''
        List all moments by pages. Admin Required.
        page -- page
        ---
        omit_serializer: true
        '''
        response = super(MomentViewSet, self).list(request)
        return SimpleResponse(response.data)

    @login_required
    def create(self, request):
        '''
        Create Moment.
        ### Request Example

            {
                "user_id": "xxx",
                "content_type": "text/pics/pics-text",
                "content": {"text": "xxx", "pics": "xxx"},
                "visible": "private/public/group_id"
            }
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body
        '''
        user_id = request.data.get('user_id')
        content_type = request.data.get('content_type')
        content = request.data.get('content')
        visible = request.data.get('visible')
        if user_id != str(request.user.id):
            return SimpleResponse(status=status.HTTP_401_UNAUTHORIZED)
        moment = MomentService.create_moment(
            user_id=user_id,
            content_type=content_type,
            content=content,
            visible=visible)
        if not moment:
            return SimpleResponse(status=status.HTTP_400_BAD_REQUEST)
        return SimpleResponse(MomentService.serialize(moment))

    @login_required
    def retrieve(self, request, id):
        '''
        Retrieve moment.
        ---
        omit_serializer: true
        '''
        moment = MomentService.get_moment(id=id)
        if not moment:
            return SimpleResponse(status=status.HTTP_404_NOT_FOUND)
        elif moment.user_id != request.user.id:
            return SimpleResponse(status=status.HTTP_401_UNAUTHORIZED)
        return SimpleResponse(MomentService.serialize(moment))

    @login_required
    def destroy(self, request, id):
        '''
        Delete moment
        ---
        omit_serializer: true
        '''
        moment = MomentService.get_moment(id=id)
        if not moment:
            return SimpleResponse(status=status.HTTP_404_NOT_FOUND)
        elif moment.user_id == request.user.id:
            return SimpleResponse(success=MomentService.delete_moment(moment))
        else:
            return SimpleResponse(status=status.HTTP_401_UNAUTHORIZED)
