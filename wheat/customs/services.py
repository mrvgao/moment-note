# -*- coding:utf-8 -*-

from collections import OrderedDict
from datetime import datetime
import hashlib
import requests

role_map = {
	'p-grandfather': u'外公',
	'p-grandmother': u'外婆',
	'm-grandfather': u'爷爷',
	'm-grandmother': u'奶奶',
	'father': u'爸爸',
	'mother': u'妈妈',
	'child': u'孩子',
    'wife': u'老婆',
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

class BaseService:

    @classmethod
    def serialize_objs(cls, obj_list, request=None):
        data = []
        for obj in obj_list:
            if request is None:
                data.append(OrderedDict(cls.serialize(obj)))
            else:
                data.append(OrderedDict(cls.serialize(obj, context={'request': request})))
        return data


class MessageService(object):

    @staticmethod
    def random_code(number):
        '''
        Gets random code from a number.
        '''
        def add_one(item):
            value = int(item) * 103 % 10
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
        software_version = '2014-06-30' # version for verification system, provided by upaas company.
        HOST = 'http://www.ucpaas.com/maap/sms/code'
        ACCOUNT_ID = '8a70971adf5ba2d4598193cc03fcbaa2'
        VER_AUTH_TOKEN = "7c7c4e5d324b7efbf75db740fdf6a253"  
        APP_ID = '71ca63be653c45129a819964265eccec'
        TEMPLATE_ID = template_id

        current_time = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3] # get time token yyyyMMddHHmmss

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

        if status == SUCCEED_MARK: # if status is 000000, send is succeed
            return True, verification_code
        else:
            return False, None

    @staticmethod
    def check_captcha(phone, captcha):
        return MessageService.random_code(phone) == captcha