# -*- coding:utf-8 -*-

from datetime import datetime
from django.db import transaction
from customs.services import BaseService
from .models import Order, Address, Pay, Delivery, Invoice
from .models import OrderSerializer, AddressSerializer
from .models import PaySerializer, DeliverySerializer, InvoiceSerializer
from customs.services import MessageService
from customs.services import role_map
from apps.moment.services import MomentService
from customs.api_tools import api
from information import redis_tools
from customs.delegates import delegate


class OrderService(BaseService):

    model = Order
    serializer = OrderSerializer


class AddressService(BaseService):

    model = Address
    serializer = AddressSerializer


class PayService(BaseService):

    model = Pay
    serializer = PaySerializer


class DeliveryService(BaseService):

    model = Delivery
    serializer = DeliverySerializer


class InvoiceService(BaseService):

    model = Invoice
    serializer = InvoiceSerializer
    

oreder_service = delegate(OrderService(), OrderService().serialize)
address_service = delegate(AddressService(), AddressService().serialize)
invoice_service = delegate(InvoiceService(), InvoiceService().serialize)
