# -*- coding:utf-8 -*-

from customs.serializers import XModelSerializer

from .models import Order, Address, Pay, Delivery, Invoice
from .models import DeliveryCarrier


class OrderSerializer(XModelSerializer):

    class Meta:
        model = Order
        fields = (
            'order_no', 'buyer_id', 'pay', 'trade_no', 'book_id', 'binding',
            'count', 'address', 'consignee', 'phone', 'invoice',
            'note', 'created_at', 'transaction_id',
            'promotion_info', 'status', 'print_info', 'update_time',
            'expired', 'deleted', 'delivery')


class AddressSerializer(XModelSerializer):

    class Meta:
        model = Address
        fields = '__all__'


class PaySerializer(XModelSerializer):

    class Meta:
        model = Pay
        exclude = ('id', )


class DeliveryCarrierSerializer(XModelSerializer):

    class Meta:
        model = DeliveryCarrier
        fields = '__all__'


class DeliverySerializer(XModelSerializer):

    class Meta:
        model = Delivery
        fields = '__all__'


class InvoiceSerializer(XModelSerializer):

    class Meta:
        model = Invoice
        fields = '__all__'
