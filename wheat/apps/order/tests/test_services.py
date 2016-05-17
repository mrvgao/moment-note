'''
Test order services
'''

from django.test import TestCase

from apps.book.models import Book
from apps.user.services import UserService
from apps.group.services import GroupService
from apps.order.services import PayService
from apps.order.services import OrderService
from apps.order.services import AddressService
from apps.order.services import InvoiceService


pay_service = PayService()
order_service = OrderService()
address_service = AddressService()
invoice_service = InvoiceService()


class TestPayService(TestCase):
    def setUp(self):
        phone = '1885745309'
        self.user = UserService().create(phone=phone+str(0), password='123456')
        self.group = GroupService().create_default_home(self.user.id)
        self.book = Book.objects.create(
            creator_id=self.user.id,
            group_id=self.group.id,
            author='minchiuan',
            page_num=100,
        )

    def test_price(self):
        price = pay_service.get_price(self.book.id, 'literary', 2, 'mailitest')
        self.assertIsNotNone(price)

        self.assertEqual(price['price'], 100*1.0)
        self.assertEqual(price['total_price'], 2 * 100 * 1.0)
        self.assertEqual(price['paid_price'], 2 * 100 * 1.0 * 0.01)

    def test_create_pay(self):
        pay = pay_service.create(self.book.id, 'literary', 2, 'wechat')
        self.assertEqual(pay.paid_price, 2 * 100 * 1.0)


class TestOrderService(TestCase):
    def setUp(self):
        phone = '1885745309'
        self.user = UserService().create(phone=phone+str(0), password='123456')
        self.group = GroupService().create_default_home(self.user.id)
        self.book = Book.objects.create(
            creator_id=self.user.id,
            group_id=self.group.id,
            author='minchiuan',
            page_num=100,
        )
        self.request_data = {
            "book_id": str(self.book.id),
            "binding": "literary",
            "count": 2,
            "buyer_id": str(self.user.id),
            "address": 'xihu strict',
            "consignee": 'minchiuan',
            "phone": '18857453090',
            "invoice": '',
            "note": 'no',
            "paid_type": "alipay",
            "promotion_info": "no",
            "delivery": "sf",
            "delivery_price": 12,
        }

    def test_create_trade_no(self):
        no = order_service.create_trade_no('1234567890123412')
        self.assertEqual(len(no), 12)

    def test_create_payment(self):
        print('test_create_payment')

        payment = order_service.create_payment(**self.request_data)

        address = AddressService().get(user_id=payment.buyer_id)
        self.assertIsNotNone(address)
        self.assertEqual(len(payment.order_no), 12)
        self.assertTrue(hasattr(payment, 'pay'))

        self.assertTrue(hasattr(payment, 'delivery'))
        self.assertEqual(payment.pay['total_price'], 2 * 100 * 1.0)

    def test_create_make_payment_info(self):
        payment = order_service.create_payment(**self.request_data)
        order_no = payment.order_no,
        total_fee = 100
        body = 'hi'
        order_info = order_service.make_payment_info(order_no, total_fee, body)
        self.assertIsNotNone(order_info)

    def test_create_sign(self):
        payment = order_service.create_payment(**self.request_data)
        sign = order_service.create_sign('alipay', payment.order_no)
        self.assertIsNotNone(sign)
        self.assertTrue('query' in sign)
        self.assertTrue('sign' in sign)
        
    def test_get_user_order(self):
        payment = order_service.create_payment(**self.request_data)

        self.request_data['count'] = 10
        payment_2 = order_service.create_payment(**self.request_data)

        orders = order_service.get_user_order(self.request_data['buyer_id'])

        self.assertEqual(len(orders), 2)
        

