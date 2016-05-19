'''
Configuration for wechat paid.

@Author Minchiuan Gao <2016-May-19>
'''

from settings import API_VERSION
URL_PREFIX = '/api/%s/' % API_VERSION

APP_ID = 'wxccf63a75e17024a4'
MCH_ID = '1343093701'

NOTIFY_URL = URL_PREFIX + 'order/wechat_notify/'
TRADE_TYPE = 'APP'

KEY = '9d5a87a59bc75dc541407a38839fd873'


