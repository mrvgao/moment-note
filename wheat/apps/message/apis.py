# -*- coding:utf-8 -*-
from apps.user.permissions import login_required
from apps.user.permissions import user_is_same_as_logined_user
from customs.response import SimpleResponse
from rest_framework.views import APIView


class Message(APIView):
    @login_required
    @user_is_same_as_logined_user
    def get(self, begin_id, step):
        '''
        获得历史信息Get History information
        '''
        return SimpleResponse(data={'test': 'succeed'})
