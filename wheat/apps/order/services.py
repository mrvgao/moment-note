# -*- coding:utf-8 -*-

from datetime import datetime
from django.db import transaction
from customs.services import BaseService
from .models import Order, Address, Pay, Delivery, Invoice
from .models import DeliveryCarrier
from .serializers import OrderSerializer, AddressSerializer
from .serializers import PaySerializer, DeliverySerializer, InvoiceSerializer
from .serializers import DeliveryCarrierSerializer
from customs.api_tools import api
from customs.delegates import delegate
from .utils.alipay import alipay_config
from .utils.alipay import alipay_handler
from .utils.wechat import wechat_handler
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

    def create_sign(self, paid_type, order_no, user_ip=None):
        order = self.get(order_no=order_no)
        if paid_type == Pay.ALIPAY:
            order_paramters = self.make_payment_info(order_no, order.pay['paid_price'], order_no)
            return alipay_handler.make_request_sign(order_paramters)
        elif paid_type == Pay.WECHAT:
            order_paramters = wechat_handler.create_paramter(
                order_no, order_no, order.pay['paid_price'], user_ip
            )
            prepay_id = wechat_handler.create_prepay(order_paramters).get('prepay_id', None)
            return prepay_id

    @api
    def create_payment(self, paid_type, **kwargs):
        book_id = kwargs['book_id']
        binding = kwargs.get('binding', Order.LITERARY)
        count = kwargs.get('count', 1)
        promotion = kwargs.get('promotion_info', None)

        pay = PayService().create(book_id, binding, count, paid_type, promotion)
        kwargs['pay_info'] = pay.id

        delivery_carrier_id = kwargs.pop('delivery_id')
        kwargs.pop('delivery_price', None)
        delivery_name = DeliveryCarrierService().get(id=delivery_carrier_id).name
        delivery_price = DeliveryCarrierService().get(id=delivery_carrier_id).price
        delivery = DeliveryService().create(delivery=delivery_name, price=delivery_price)
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

        invoice = kwargs.get('invoice', None)
        if invoice:
            InvoiceService().add(user_id=buyer_id, invoice=invoice)
        
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

    def check_wechat_recall(self, xml_doc):
        '''
        valid wechat recall xml if is valid.
        '''

        paramter = wechat_handler.xml_to_dict(xml_doc)
        valid = wechat_handler.verify_wechat_recall_info(paramter)

        if valid:
            out_trade_no = paramter['out_trade_no']
            transaction_id = paramter['transaction_id']
            self.valid_wechat_pay(out_trade_no, transaction_id)

        echo = {'return_code': None}

        if valid:
            echo['return_code'] = 'SUCCESS'
        else:
            echo['return_code'] = 'FAIL'

        return wechat_handler.dict_to_xml('xml', echo)

    def unpaid(self, order):
        unpaid_staus = ['unpaid']
        return order.status in unpaid_staus

    def valid_wechat_pay(self, order_no, transcation_id):
        order = self.get(order_no=order_no)
        if self.unpaid(order):
            self.update(order, transaction_id=transcation_id)
            self.update(order, status=Order.PAID)
            pay = PayService().get(id=order.pay_info)
            PayService().update(pay, paid=True, paid_time=datetime.now())
        return True


class AddressService(BaseService):

    model = Address
    serializer = AddressSerializer

    def set_default(self, user_id, address_id, args):
        if args.get('is_default', None):
            self.list(user_id).exclude(id=address_id).update(is_default=False)

    @api
    def create(self, **kwargs):
        address = super(AddressService, self).create(**kwargs)
        id = address.id
        user_id = address.user_id
        self.set_default(user_id, id, kwargs)
        return address

    @api
    def update_by_id(self, id, **kwargs):
        address = super(AddressService, self).update_by_id(id, **kwargs)

        self.set_default(address.user_id, id, kwargs)

        return address

    @api
    def list(self, user_id):
        addresses = self.get(user_id=user_id, deleted=False, many=True)

        if addresses:
            return addresses.order_by('-is_default')
        else:
            return None

    @api
    def delete_by_id(self, id):
        return super(AddressService, self).delete_by_id(id)


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


class DeliveryCarrierService(BaseService):

    model = DeliveryCarrier
    serializer = DeliveryCarrierSerializer

    def create_default(self):
        default = {'name': '其他', 'price': 0}
        return DeliveryCarrier.objects.create(**default)
        
    def get(self, **kwargs):
        carrier = super(DeliveryCarrierService, self).get(**kwargs)

        if not carrier:
            return self.create_default()
        else:
            return carrier

    def get_by_id(self, id):
        carrier = self.get(id=id)
        return carrier

    @api
    def get_all(self):
        return self.get(deleted=False, many=True)

    @api
    def create(self, **kwargs):
        return super(DeliveryCarrierService, self).create(**kwargs)
    

class DeliveryService(BaseService):

    model = Delivery
    serializer = DeliverySerializer


class InvoiceService(BaseService):

    model = Invoice
    serializer = InvoiceSerializer

    @api
    def create(self, **kwargs):
        return super(InvoiceService, self).create(**kwargs)

    @api
    def list(self, user_id):
        orders = self.get(many=True, deleted=False, user_id=user_id)
        return orders

    @api
    def update_by_id(self, id, **kwargs):
        return super(InvoiceService, self).update_by_id(id, **kwargs)

    @api
    def get_by_id(self, id):
        return self.get(id=id)

    @api
    def delete_by_id(self, id):
        return super(InvoiceService, self).delete_by_id(id)


order_service = delegate(OrderService(), OrderService().serialize)
pay_service = delegate(PayService(), PayService().serialize)
address_service = delegate(AddressService(), AddressService().serialize)
invoice_service = delegate(InvoiceService(), InvoiceService().serialize)
delivery_carrier_service = delegate(DeliveryCarrierService(), DeliveryCarrierService().serialize)
delivery_service = delegate(DeliveryService(), DeliveryService().serialize)
