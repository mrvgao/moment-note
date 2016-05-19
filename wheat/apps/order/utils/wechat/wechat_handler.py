'''
Main Handler of Wechat Pay.

@Author Minchiuan Gao <2016-May-19>
'''

import requests
import wechat_config
from random import Random
import md5
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import tostring
from django.utils.encoding import smart_str, smart_unicode
import xml.etree.ElementTree as ET


def create_paramter(trade_no, describe, total_fee, create_ip):
    paramter = {
        'body': describe,
        'appid': wechat_config.APP_ID,
        'mch_id': wechat_config.MCH_ID,
        'nonce_str': random_str(),
        #'nonce_str': 'ngtrql5dp9fypl1s53yldi7gkccra6o6',
        'out_trade_no': trade_no,
        'total_fee': int(total_fee * 100),  # units as cents, so need * 100.
        'spbill_create_ip': create_ip,
        'notify_url': wechat_config.NOTIFY_URL,
        'trade_type': wechat_config.TRADE_TYPE,
    }

    paramter['sign'] = get_sign(paramter)

    return paramter


def create_prepay(paramter):
    WECHAT_URL = 'https://api.mch.weixin.qq.com/pay/unifiedorder'

    xml_doc = dict_to_xml('xml', paramter)
    response = requests.post(WECHAT_URL, xml_doc)

    response = xml_to_dict(response.content)

    return response


def random_str(randomlength=32):
    str = ''
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


def get_sign(paramter):
    keys = []
    for key in paramter:
        keys.append(key)

    keys.sort()

    joined_string = '&'.join(['%s=%s' % (key.lower(), paramter[key]) for key in keys])
    joined_string += '&key=' + wechat_config.KEY

    m = md5.new()
    m.update(joined_string)
    sign = m.hexdigest().upper()

    return sign


def dict_to_xml(tag, d):
    elem = Element(tag)
    for key, val in d.items():
        child = Element(key)
        child.text = str(val)
        elem.append(child)

    return tostring(elem)
    

def xml_to_dict(raw_str):
    raw_str = smart_str(raw_str)
    msg = {}
    root_elem = ET.fromstring(raw_str)
    if root_elem.tag == 'xml':
        for child in root_elem:
            msg[child.tag] = smart_unicode(child.text)
        return msg
    else:
        return None


def verify_wechat_recall_info(paramter):
    recall_sign = paramter.pop('sign', None)
    sign = get_sign(paramter)
    if sign == recall_sign and paramter['return_code'] == 'SUCCESS':
        return True
    else:
        return False
    

def test():
    trade_no = 'ASF1234DAFE1'
    describe = 'test wechat'
    total_fee = 10 * 100
    create_ip = '121.40.158.110'
    parameter = create_paramter(trade_no, describe, total_fee, create_ip)
    create_prepay(parameter)

if __name__ == '__main__':
    test()
    

