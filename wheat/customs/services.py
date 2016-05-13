# -*- coding:utf-8 -*-

from collections import OrderedDict
from datetime import datetime
import hashlib
import requests
from django.db import transaction
import sys

role_map = {
    'm-grandfather': u'外公',
    'm-grandmother': u'外婆',
    'f-grandfather': u'爷爷',
    'f-grandmother': u'奶奶',
    'father': u'爸爸',
    'mother': u'妈妈',
    'child': u'孩子',
    'wife': u'老婆',
    'husband': '老公',
    'son': u'儿子',
    'daughter': u'女儿',
    'slibe': u'哥哥/弟弟',
    'sister': u'姐姐／妹妹',
    'l-father': '公公',
    'l-mother': '婆婆',
    'suocero': '岳父',
    'suocera': '岳母',
    'qj-g': '亲家母',
    'qj-m': '亲家公',
    'l-son': '女婿',
    'self': 'self'
}


class BaseService(object):
    '''
    Base class of every service.
    '''
    model = None
    serializer = None

    __api__ = False

    def get_model(self):
        return self.model

    def get_serializer(self):
        return self.serializer

    def exist(self, *arg, **kwargs):
        return self.model.objects.filter(*arg, **kwargs).exists()

    @transaction.atomic
    def create(self, **kwargs):
        fields = self.filter_read_only_field(**kwargs)
        new_obj = self.model(**fields)
        new_obj.save()
        return new_obj

    @transaction.atomic
    def update_by_id(self, id, **kwargs):
        return self.update(self.get(id=id), **kwargs)

    @transaction.atomic
    def update(self, instance, **kwargs):
        update_fields = self.filter_read_only_field(**kwargs)
        new_obj = instance.update(**update_fields)
        # notice, the arg to seriazer's update is a dictionary
        new_obj.save()
        return new_obj

    def get(self, *arg, **kwargs):

        many = kwargs.pop('many', False)

        result = None

        if self.exist(*arg, **kwargs):
            result = self.model.objects.filter(*arg, **kwargs)
            if not many:
                result = result.first()

        return result

    def serialize(self, obj):
        many = False
        
        try:
            iter(obj)
        except TypeError:
            # this is a single obj
            pass 
        else:
            many = True

        return self.serializer(obj, many=many).data if obj else None

    def delete(self, instance):
        DELETED = 'deleted'
        if hasattr(instance, DELETED):
            setattr(instance, DELETED, True)
            instance.save()
        else:
            raise ReferenceError('cannot delete this obj in db, use deleted = True')

        return instance

    @classmethod
    def filter_read_only_field(cls, **kwargs):
        '''
        Delete the read only field in kwargs. To protect data not be changed by
        normal user.
        '''
        if hasattr(cls.serializer.Meta, 'read_only_fields'):
            read_only_fields = cls.serializer.Meta.read_only_fields
        else:
            read_only_fields = ()

        update_fields = {k: v for k, v in kwargs.iteritems() if k not in read_only_fields}

        return update_fields

    @classmethod
    def api_json_method(cls, func):
        def check_result(**kwargs):
            result = func(**kwargs)
            if isinstance(result, dict):
                return result
            else:
                return cls.seriaze(result)
        return check_result


class MessageService(object):

    temp_captcha = '12750'
    temp_invitation = '20721'

    @staticmethod
    def send_captcha(phone, captcha):
        success = MessageService.post_message(phone, MessageService.temp_captcha, captcha)
        return success

    @staticmethod
    def send_invitation(phone, inviter, message, role):
        chinese_role = role_map.get(role, 'hi')
        maili_url = 'http://www.mailicn.com'
        message = message or 'hi'
        msg_string = chinese_role + '， ' + message
        nickname = '(%s)%s' % (inviter.phone, inviter.nickname)
        send_message_param = '%s,%s,%s' % (msg_string, nickname, maili_url)

        success = MessageService.post_message(
            phone,
            MessageService.temp_invitation,
            send_message_param)

        return success
        
    @staticmethod
    def post_message(phone, template_id, message_param):
        HOST = 'http://www.ucpaas.com/maap/sms/code'
        APP_ID = '71ca63be653c45129a819964265eccec'
        TEMPLATE_ID = template_id

        ACCOUNT_ID = '8a70971adf5ba2d4598193cc03fcbaa2'
        VER_AUTH_TOKEN = "7c7c4e5d324b7efbf75db740fdf6a253"
        m = hashlib.md5()
        current_time = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
        # get time token yyyyMMddHHmmss
        m.update(ACCOUNT_ID + current_time + VER_AUTH_TOKEN)
        sig_md5_code = m.hexdigest()

        post_message = {
            'sid': ACCOUNT_ID,
            'appId': APP_ID,
            'sign': sig_md5_code,
            'time': current_time,
            'templateId': TEMPLATE_ID,
            'to': phone,
            'param': message_param
        }

        SUCCEED_MARK = '000000'

        if 'customs' in sys.argv:  # send message only when test customs.
            response = requests.post(HOST, data=post_message, verify=False)
            status = response.json()['resp']['respCode']
        else:
            status = SUCCEED_MARK

        if status == SUCCEED_MARK:  # if status is 000000, send is succeed
            return True
        else:
            return False
