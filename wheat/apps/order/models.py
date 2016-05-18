# -*- coding:utf-8 -*-
import uuid
from uuidfield import UUIDField
from django.db import models

from customs.models import EnhancedModel, CommonUpdateAble


class Order(CommonUpdateAble, models.Model, EnhancedModel):

    LITERARY = 'literary'
    ECONOMIC = 'economic'
    HARDCOVER = 'hardcover'

    BINDING = (
        (LITERARY, LITERARY),
        (ECONOMIC, ECONOMIC),
        (HARDCOVER, HARDCOVER),
    )

    PAID = 'paid'

    ORDER_STATUS = (
        ('待支付', 'unpaid'),
        ('已支付', PAID),
        ('等待印刷', 'unprinted'),
        ('正在印刷', 'printing'),
        ('已发货', 'deliveried'),
        ('已收获', 'received'),
    )

    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_no = models.CharField(max_length=30, unique=True, db_index=True, default="")
    buyer_id = UUIDField(db_index=True)
    book_id = UUIDField(db_index=True)
    binding = models.CharField(max_length=10, choices=BINDING)
    count = models.IntegerField(default=1)
    address = models.CharField(max_length=50)
    consignee = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    invoice = models.CharField(max_length=50)
    note = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(auto_now_add=True)
    trade_no = models.CharField(max_length=50, default="")  # for alipay and wechat
    transaction_id = models.CharField(max_length=50, default="")
    promotion_info = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=50, choices=ORDER_STATUS, default='unpaid')
    print_info = models.CharField(max_length=200, default="")  # appending info.
    pay_info = UUIDField(db_index=True)
    update_time = models.DateTimeField(auto_now_add=True)
    delivery_info = UUIDField(db_index=True, null=True, default=None)
    expired = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    @property
    def pay(self):

        try:
            pay = Pay.objects.get(id=self.pay_info)
        except Exception:
            return {}
        else:
            return {
                'price': pay.price,
                'total_price': pay.total_price,
                'paid_price': pay.paid_price,
                'paid_type': pay.paid_type,
                'paid_time': pay.paid_time,
                'paid_finish': pay.paid,
            }

    @property
    def delivery(self):

        try:
            delivery = Delivery.objects.get(id=self.delivery_info)
        except Exception:
            return {}
        else:
            return {
                'delivery': delivery.delivery,
                'delivery_no': delivery.delivery_no,
                'delivery_time': delivery.delivery_time,
                'update_time': delivery.update_time,
                'status': delivery.status,
            }

    class Meta:
        db_table = "order"


class Pay(CommonUpdateAble, models.Model, EnhancedModel):

    ALIPAY = 'alipay'
    WECHAT = 'wechat'

    PAID_TYPE = (
        (ALIPAY, ALIPAY),
        (WECHAT, WECHAT),
    )

    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    price = models.FloatField(default=0.0)
    total_price = models.FloatField(default=0.0)
    paid_price = models.FloatField(default=0.0)
    paid_type = models.CharField(max_length=20, choices=PAID_TYPE)
    paid_time = models.DateTimeField(null=True)
    paid = models.BooleanField(default=False)

    class Meta:
        db_table = "order_pay"


class DeliveryCarrier(CommonUpdateAble, models.Model, EnhancedModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)  # 物流公司
    price = models.IntegerField(default=0)
    deleted = models.BooleanField(default=False)
    

class Delivery(CommonUpdateAble, models.Model, EnhancedModel):
    UNSENT = ('unsend', '未发货')
    SENT = ('send', '已发货')
    ON_THE_WAY = ('on-the-way', '在途中')

    STATUS = (
        UNSENT,
        SENT,
        ON_THE_WAY,
    )

    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delivery = models.CharField(max_length=20)  # 物流公司
    price = models.IntegerField(default=0)
    delivery_no = models.CharField(max_length=50, null=True)   # 物流单号
    delivery_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now_add=True)  # 最后一次信息更新时间, 用于跟踪货物
    status = models.CharField(max_length=100, choices=STATUS, default=UNSENT[1])  # 物流状态, eg. 正在西湖区派件中心 etc.

    class Meta:
        db_table = "order_delivery"


class Address(CommonUpdateAble, models.Model, EnhancedModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = UUIDField(db_index=True)
    consignee = models.CharField(max_length=50, default="")
    phone = models.CharField(max_length=20)
    zip_code = models.CharField(max_length=10, null=True)
    address = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    update_time = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_address'


class Invoice(CommonUpdateAble, models.Model, EnhancedModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = UUIDField(db_index=True)
    order_id = models.CharField(max_length=50, db_index=True, null=True, default="")
    invoice = models.CharField(max_length=100, default="")
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'invoice'
