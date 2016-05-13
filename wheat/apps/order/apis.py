# -*- coding:utf-8 -*-
from customs import class_tools
from customs import request_tools
from errors import codes
from customs.response import APIResponse
from .service import order_service
from .service import address_service
from .service import invoice_service
from rest_framework import viewsets, status


@class_tools.set_service(order_service)
class OrderViewSet(viewsets.GenericViewSet):

    def create(self, request):
        pass

    def notify(self, request):
        pass

    def retrieve(self, reqeust, id):
        pass

    def update(self, request, id):
        pass
    

@class_tools.set_service(address_service)
class AddressViewSet(viewsets.AddressService):

    def create(self, request):
        pass


@class_tools.set_service(invoice_service)
class InvoiceViewSet(viewsets.GenericViewSet):

    def create(self, request):
        pass

    def list(self, request):
        pass

    def delete(self, request, id):
        pass
        
