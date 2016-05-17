# -*- coding:utf-8 -*-

from datetime import datetime
from django.db import transaction
from customs.services import BaseService
from .models import Order, Address, Pay, Delivery, Invoice
from .serializers import OrderSerializer, AddressSerializer
from .serializers import PaySerializer, DeliverySerializer, InvoiceSerializer
from customs.api_tools import api
from customs.delegates import delegate
from .utils.alipay import alipay_config
from .utils.alipay import alipay_handler
from apps.book.services import BookService


class OrderService(BaseService):

    model = Order
    serializer = OrderSerializer

    def make_payment_info(self, order_no, total_fee, body):
        if total_fee < 0.01:
            total_fee = 0.01
            
        order_info = {
            "partner": "%s" % (alipay_config.partner_id),
            "service": "mobile.securitypay.pay",
            "_input_charset": "utf-8",
            "notify_url": "%s" % (alipay_config.recall_host),
            "out_trade_no": str(order_no),
            "paymnet_type": "1",
            "subject": str(order_no),
            "seller_id": alipay_config.alipay_account,
            "total_fee": total_fee,
            "body": body,
        }

        return order_info

    def create_sign(self, paid_type, order_no):
        order = self.get(order_no=order_no)
        if paid_type == Pay.ALIPAY:
            order_paramters = self.make_payment_info(order_no, order.pay['paid_price'], order_no)
            return alipay_handler.make_request_sign(order_paramters)

    @api
    def create_payment(self, paid_type, **kwargs):
        book_id = kwargs['book_id']
        binding = kwargs.get('binding', Order.LITERARY)
        count = kwargs.get('count', 1)
        promotion = kwargs.get('promotion_info', None)

        pay = PayService().create(book_id, binding, count, paid_type, promotion)
        kwargs['pay_info'] = pay.id

        delivery = kwargs.pop('delivery')
        delivery_price = kwargs.pop('delivery_price', 0)
        delivery = DeliveryService().create(delivery=delivery, price=delivery_price)
        kwargs['delivery_info'] = delivery.id

        address = kwargs.get('address')
        buyer_id = kwargs.get('buyer_id')
        address = kwargs.get('address')
        consignee = kwargs.get('consignee')
        phone = kwargs.get('phone')

        if not AddressService().get(user_id=buyer_id, address=address, consignee=consignee):
            AddressService().create(
                user_id=buyer_id,
                consignee=consignee,
                phone=phone,
                address=address,
            )

        order = self.create(**kwargs)
        trade_no = self.create_trade_no(order.id)
        self.update(order, order_no=trade_no)
        
        return order

    @api
    def get_user_order(self, user_id):
        orders = self.get(buyer_id=user_id, deleted=False, many=True)
        return orders

    @api
    def retrieve(self, order_no):
        order = self.get(order_no=order_no)
        return order

    @api
    def delete_order(self, order_no):
        order = self.get(order_no=order_no)
        order = self.delete(order)
        return order

    @api
    def update_order(self, order_no, **kwargs):
        order = self.get(order_no=order_no)
        return self.update(order, **kwargs)

    def create_trade_no(self, uuid):
        trade_no_length = 12
        return str(str(uuid)[:trade_no_length]).upper()
        
    def check_params(self, params):
        valid = alipay_handler.verify_recall_info(params)

        return valid

    def valid_order(self, order_no, trade_no):
        order = self.get(order_no=order_no)
        if order:
            self.update(order, trade_no=trade_no)
            self.update(order, status=Order.PAID)
            pay = PayService().get(id=order.pay_info)
            PayService().update(pay, paid=True, paid_time=datetime.now())
        else:
            print('order no not found')
        return True


class AddressService(BaseService):

    model = Address
    serializer = AddressSerializer

    @api
    def create(self, **kwargs):
        return super(AddressService, self).create(**kwargs)

    @api
    def update_by_id(self, id, **kwargs):
        address = super(AddressService, self).update_by_id(id, **kwargs)
        return address

    @api
    def list(self, user_id):
        addresses = self.get(user_id=user_id, deleted=False, many=True)
        return addresses

    @api
    def delete(self, id):
        return super(AddressService, self).delete(id)


class PayService(BaseService):

    model = Pay
    serializer = PaySerializer

    def create(self, book_id, binding, count, paid_type, promotion_info=None):
        assert paid_type in [Pay.ALIPAY, Pay.WECHAT], 'paid type error'

        price = self.get_price(book_id, binding, count, promotion_info)

        pay = super(PayService, self).create(
            price=price['price'],
            total_price=price['total_price'],
            paid_price=price['paid_price'],
            paid_type=paid_type,
        )

        return pay

    def get_price(self, book_id, binding, count, promotion_info=None):
        count = int(count)
        binding_price = {
            Order.LITERARY: 1.0,
            Order.ECONOMIC: 1.1,
            Order.HARDCOVER: 1.2,
        }

        assert binding in binding_price, 'binding type unacceptable'
        book = BookService.get_book(id=book_id)

        if book:
            page_num = book.page_num
            assert page_num > 0, 'page cannot less than 1'
            price = page_num * binding_price[binding]
            total_price = price * count
            paid_price = self.promotion(total_price, promotion_info)
        else:
            price = -1
            total_price = -1
            paid_price = -1

        return {
            'price': price,
            'total_price': total_price,
            'paid_price': paid_price,
        }

    def promotion(self, total_price, promotion=None):
        if promotion == 'mailitest':
            return total_price * 0.01
        return total_price


class DeliveryService(BaseService):

    model = Delivery
    serializer = DeliverySerializer


class InvoiceService(BaseService):

    model = Invoice
    serializer = InvoiceSerializer


order_service = delegate(OrderService(), OrderService().serialize)
pay_service = delegate(PayService(), PayService().serialize)
address_service = delegate(AddressService(), AddressService().serialize)
invoice_service = delegate(InvoiceService(), InvoiceService().serialize)
