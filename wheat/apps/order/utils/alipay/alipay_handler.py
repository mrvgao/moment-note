# -*- coding:utf-8 -*-

'''
Alipay Handler.

@Author Minchiuan Gao <2015-May-14>
'''

import rsa
import base64
from . import alipay_config
import urllib
import requests


def params_to_query(params):
    '''
    Change dict to &+& query paramter.
    '''
    query = ""
    for key in sorted(params.keys(), reverse=False):
        value = params[key]
        query += '{0}="{1}"&'.format(str(key), str(value))

    query = query[:-1]  # delete the last '&'

    return query


def make_sign(string):
    private_key = rsa.PrivateKey._load_pkcs1_pem(alipay_config.private_key)
    sign = rsa.sign(string, private_key, alipay_config.sign_type)
    b64string = base64.b64encode(sign)
    return b64string


def make_request_sign(param_dict):
    query = params_to_query(param_dict)
    sign = make_sign(query)
    sign = urllib.quote_plus(sign)
    return {
        'query': query,
        'sign': sign,
    }


def query_to_dict(query):
    res = {}
    k_v_pairs = query.split("&")
    for item in k_v_pairs:
        sp_item = item.split("=", 1)
        # 注意，因为sign秘钥里面肯那个包含'='符号，所以splint一次就可以了
        key = sp_item[0]
        value = sp_item[1]
        res[key] = value

        return res


def check_ali_sign(message, sign):
    sign = base64.b64decode(sign)
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(alipay_config.alipay_public_key)

    correct = False

    try:
        correct = rsa.verify(message, sign, pubkey)
    except Exception as e:
        print e
        correct = False

    return correct


def verify_from_alipay(partner_id, notify_id):
    alipay_gateway_url = 'https://mapi.alipay.com/gateway.do'

    verify_info = {
        'service': 'notify_verify',
        'partner': partner_id,
        'notify_id': notify_id,
    }

    response = requests.get(alipay_gateway_url, params=verify_info)

    if response.text.upper() == 'TRUE':
        return True
    return False


def verify_recall_info(recall_paramters):
    check_sign = params_to_query(recall_paramters)
    params = query_to_dict(check_sign)
    # alipay need sorted param. this two step is for sort.
    del params['sign_type']
    sign = params.pop('sign')
    message = params_to_query(params)

    valid = check_ali_sign(message, sign)
    from_alipay = verify_from_alipay(alipay_config.partner_id, recall_paramters['notify_id'])

    return valid and from_alipay


