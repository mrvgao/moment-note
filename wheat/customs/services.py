# -*- coding:utf-8 -*-

from collections import OrderedDict
from datetime import datetime
import hashlib
import requests
from django.db import transaction

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
    'slibe':u'哥哥/弟弟',
    'sister':u'姐姐／妹妹',
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

    def get_model(self):
        return self.model

    def get_serializer(self):
        return self.serializer

    def exist(self, **kwargs):
        return self.model.objects.filter(**kwargs).exists()

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

    def get(self, many=False, **kwargs):
        if not self.exist(**kwargs):
            return None
        else:
            if many:
                return self.model.objects.filter(**kwargs)
            else:
                return self.model.objects.filter(**kwargs)[0]

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
    @staticmethod
    def random_code(number, plus=0):
        '''
        Gets random code from a number.
        '''
        def add_one(item):
            value = int(item) * (103 + plus) % 10
            return str(value)

        number = map(add_one, number[-6:])
        return ''.join(number)

    @staticmethod
    def send_message(phone='18857453090', template_id='12750', message_param=None, send=True):
        '''
        Sends verification message to a specific phone number.

        Author: Minchiuan 2016-2-22

        Return:
            (send_if_succeed, verification code)
            if succeed, return (ture, ******)
            else return (false, None)
        '''
        software_version = '2014-06-30'
        # version for verification system, provided by upaas company.

        HOST = 'http://www.ucpaas.com/maap/sms/code'
        ACCOUNT_ID = '8a70971adf5ba2d4598193cc03fcbaa2'
        VER_AUTH_TOKEN = "7c7c4e5d324b7efbf75db740fdf6a253"
        APP_ID = '71ca63be653c45129a819964265eccec'
        TEMPLATE_ID = template_id

        current_time = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
        # get time token yyyyMMddHHmmss

        m = hashlib.md5()
        m.update(ACCOUNT_ID + current_time + VER_AUTH_TOKEN)
        sig_md5_code = m.hexdigest()

        verification_code = MessageService.random_code(phone)

        if message_param is None:
            message_param = verification_code

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

        if send:
            response = requests.post(HOST, data=post_message, verify=False)
            status = response.json()['resp']['respCode']
        else:
            status = SUCCEED_MARK

        if status == SUCCEED_MARK:  # if status is 000000, send is succeed
            return True, verification_code
        else:
            return False, None

    @staticmethod
    def check_captcha(phone, captcha):
        return MessageService.random_code(phone) == captcha
