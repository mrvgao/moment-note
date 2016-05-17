# -*- coding:utf-8 -*-

from customs.serializers import XModelSerializer

from .models import Order, Address, Pay, Delivery, Invoice


class OrderSerializer(XModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'
        exclude = ('id', 'deleted', 'pay_info')


class AddressSerializer(XModelSerializer):

    class Meta:
        model = Address
        fields = '__all__'


class PaySerializer(XModelSerializer):

    class Meta:
        model = Pay
        exclude = ('id', )


class DeliverySerializer(XModelSerializer):

    class Meta:
        model = Delivery
        fields = '__all__'


class InvoiceSerializer(XModelSerializer):

    class Meta:
        model = Invoice
        fields = '__all__'
