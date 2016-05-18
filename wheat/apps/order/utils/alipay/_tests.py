# -*- coding: utf-8 -*-

'''
Alipay test cases.

@Author Minchiuan Gao <2016-May-14>
'''

from django.test import TestCase
from . import alipay_handler
from . import alipay_config
import urllib


class TestAlipayHandler(TestCase):
    def test_param_to_query(self):
        parameters = {
            "service": "mobile.securitypay.pay",
            "partner": "2088101568338364",
            "_input_charset": "utf-8",
            "notify_url": "http://notify.msp.hk/notify.htm",
            "out_trade_no": "0819145412-6177",
            "subject": "《暗黑破坏神3:凯恩之书》",
            "payment_type": "1",
            "seller_id": "alipay-test01@alipay.com",
            "total_fee": "0.01"
        }

        query = alipay_handler.params_to_query(parameters)
        print(query)
        self.assertFalse(query.endswith('&'))

    def test_make_sign(self):
        order_desc = '''partner="%s"&seller_id="admin@mailicn.com"&out_trade_no="01A4Y6HMX24M2LS"&subject="1"&body="我是测试数据"&total_fee="0.01"&notify_url="http://www.xxx.com"&service="mobile.securitypay.pay"&payment_type="1"&_input_charset="utf-8"&it_b_pay="30m"&show_url="m.alipay.com"''' % alipay_config.partner_id

        correct_sign = "R0WZ6pKlyk0aNUeaEqBxC4m8zDXB0TPUiwlCvUxqL6NAQhwiDCKGJREF6FfXXjOazbHFrj1vwpkRk5mpVBwHF6uzJSeTobEXSQbhfVFE3sEbWUEwh0Cd9NsU0QFHfEJ7U656m8qJJXTrGGmqkj%2FGY9YCZ6iASHUR3Cv2qBzHbEY%3D"

        sign = urllib.quote_plus(alipay_handler.make_sign(order_desc))
        self.assertEqual(sign, correct_sign)

    def test_make_request_sign(self):
        params = {'service': 'test'}
        sign = alipay_handler.make_request_sign(params)
        self.assertIsNotNone(sign)

    def test_query_to_dict(self):
        recall_info = 'discount=0.00&payment_type=8&subject=测试&trade_no=2013082244524842&buyer_email=dlwdgl@gmail.com&gmt_create=2013-08-22 14:45:23&notify_type=trade_status_sync&quantity=1&out_trade_no=082215222612710&seller_id=2088501624816263&notify_time=2013-08-22 14:45:24&body=测试测试&trade_status=TRADE_SUCCESS&is_total_fee_adjust=N&total_fee=1.00&gmt_payment=2013-08-22 14:45:24&seller_email=xxx@alipay.com&price=1.00&buyer_id=2088602315385429&notify_id=64ce1b6ab92d00ede0ee56ade98fdf2f4c&use_coupon=N&sign_type=RSA&sign=1glihU9DPWee+UJ82u3+mw3Bdnr9u01at0M/xJnPsGuHh+JA5bk3zbWaoWhU6GmLab3dIM4JNdktTcEUI9/FBGhgfLO39BKX/eBCFQ3bXAmIZn4l26fiwoO613BptT44GTEtnPiQ6+tnLsGlVSrFZaLB9FVhrGfipH2SWJcnwYs='

        paramters = alipay_handler.query_to_dict(recall_info)
        self.assertTrue(isinstance(paramters, dict))


class TestAlipayConfig(TestCase):
    def test_get_key(self):
        private_key = alipay_config.private_key
        public_key = alipay_config.public_key

        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
