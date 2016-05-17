# -*- coding:utf-8 -*- import logging
from customs import class_tools
from customs import request_tools
from errors import codes
from customs.response import APIResponse
from .services import order_service
from .services import address_service
from .services import invoice_service
from .services import pay_service
from rest_framework import viewsets, status
from rest_framework.decorators import list_route, detail_route
from customs.viewsets import ListModelMixin

from apps.user.permissions import login_required

import logging
logger = logging.getLogger('order')


@class_tools.set_service(order_service)
class OrderViewSet(viewsets.ViewSet):

    @login_required
    @request_tools.post_data_check(['book_id', 'buyer_id', 'paid_type'])
    def create(self, request):
        '''
        Creates Order
        ### Request Example

            {
                "book_id": {String},
                "binding": <"literary", "econimic", "handcover">,
                "count": {Int},
                "buyer_id": {String},
                "address": {String},
                "consignee": {String},
                "phone": {String},
                "invoice": {String},
                "note": {String},
                "paid_type": <"alipay", "wechat">,
                "transcation_id": [{String}], // could be null, for wechat.
                "promotion_info": {String},
                "delivery": <"顺丰", "其他">, // required
                "delivery_price": {int}, //required
            }
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body
        '''

        kwargs = request.data
        paid_type = kwargs.pop('paid_type')

        order = order_service.create_payment(paid_type, **kwargs)

        result = {
            'order': order,
        }

        sign = order_service.create_sign(paid_type, order['order_no'])
        result['sign'] = sign

        return APIResponse(result)

    @list_route(methods=['post'])
    def notify(self, request):
        '''
        ---
        omit_serializer: true
        omit_parameters:
            - form
        parameters:
            - name: body
              paramType: body
        '''
        logger.info('notification: ' + str(request.data))
        request_data = request_tools.change_unicode_to_str(request.data)
        valid = order_service.check_params(request_data)
        logger.info(valid)
        if valid:
            order_service.valid_order(
                order_no=request_data['out_trade_no'],  # order number self defined
                trade_no=request_data['trade_no'],  # trade no alipay given.
            )

        return APIResponse({})

    @login_required
    def list(self, request):
        '''
        Get Current User's All order list.
        Return value is a list.
        ---
        omit_serializer: true
        '''
        user_id = request.user.id
        orders = order_service.get_user_order(user_id)
        return APIResponse(orders)

    def retrieve(self, reqeust, id):
        '''
        Get order info by order No.
        '''
        order = order_service.retrieve(order_no=id)

        if order:
            return APIResponse(order)
        else:
            return APIResponse(status_code=404)

    def update(self, request, id):
        '''
        Update order info by order No.
        '''
        order = order_service.update_order(order_no=id, **request.data)

        if order:
            return APIResponse(order)
        else:
            return APIResponse(status_code=404)

    def destroy(self, request, id):
        order = order_service.delete_order(order_no=id, **request.data)

        if order:
            return APIResponse(order)
        else:
            return APIResponse(status_code=404)


@class_tools.set_service(address_service)
class AddressViewSet(viewsets.GenericViewSet):

    def create(self, request):
        pass

    def update(self, request, id):
        pass

    def list(self, request):
        pass

    def delete(self, request, id):
        pass


@class_tools.set_service(invoice_service)
class InvoiceViewSet(viewsets.GenericViewSet):

    def create(self, request):
        pass

    def list(self, request):
        pass

    def delete(self, request, id):
        pass


@class_tools.set_service(pay_service)
class PriceViewSet(viewsets.GenericViewSet):
    @list_route(methods=['get'])
    def count(self, request):
        '''
        Get books totoal price.

        book_id -- book_id
        count -- count
        binding -- binding literary | economic | hardcover
        promotion_info -- if is 'mailitest', will * 0.01
        ---
        omit_serializer: true
        '''

        price = pay_service.get_price(
            request.query_params.get('book_id'),
            request.query_params.get('binding'),
            request.query_params.get('count'),
            request.query_params.get('promotion_info', None),
        )

        return APIResponse(price)
