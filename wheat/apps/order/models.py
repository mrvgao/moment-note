# -*- coding:utf-8 -*-
import uuid
from uuidfield import UUIDField
from django.db import models

from customs.models import EnhancedModel, CommonUpdateAble


class Order(CommonUpdateAble, models.Model, EnhancedModel):

    BINGDING = (
        ('literary', 'literary'),
        ('economic', 'economic'),
        ('hardcover', 'hardcover'),
    )

    ORDER_STATUS = (
        ('待支付', 'unpaid'),
        ('已支付', 'paid'),
        ('等待印刷', 'unprinted'),
        ('正在印刷', 'printing'),
        ('已发货', 'deliveried'),
        ('已收获', 'received'),
    )

    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_no = models.CharField(max_length=30, unique=True, db_index=True)
    book_id = UUIDField(db_index=True)
    binding = models.CharField(max_length=10, choices=BINGDING)
    count = models.IntegerField(default=1)
    address = models.CharField(max_length=50)
    consignee = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    invoice = models.CharField(max_length=50)
    note = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(auto_now_add=True)
    trade_no = models.CharField(max_length=50, default="")
    transacition_id = models.CharField(max_length=50, default="")
    promotion_info = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=ORDER_STATUS)
    print_info = models.CharField(max_length=200, default="")  # appending info.
    pay_info = UUIDField(db_index=True)
    update_time = models.DateTimeField(auto_now_add=True)
    delivery_info = UUIDField(db_index=True)
    exipred = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "order"


class Pay(CommonUpdateAble, models.Model, EnhancedModel):
    
    PAID_TYPE = (
        ('alipay', 'alipay'),
        ('wechat', 'wechat'),
    )

    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    price = models.FloatField(default=0.0)
    total_price = models.FloatField(default=0.0)
    paid_price = models.FloatField(default=0.0)
    paied_type = models.CharField(max_length=20, choices=PAID_TYPE)
    paid_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_pay"


class Delivery(CommonUpdateAble, models.Model, EnhancedModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delivery = models.CharField(max_length=20)  # 物流公司
    delivery_no = models.CharField(max_length=50)   # 物流单号
    delivery_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now_add=True)  # 最后一次信息更新时间, 用于跟踪货物
    status = models.CharField(max_length=100)  # 物流状态, eg. 正在西湖区派件中心 etc.

    class Meta:
        db_table = "order_delivery"


class Address(CommonUpdateAble, models.Model, EnhancedModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = UUIDField(db_index=True)
    consignee = models.CharField(max_length=50, default="")
    phone = models.CharField(max_length=20)
    zip_code = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_address'


class Invoice(CommonUpdateAble, models.Model, EnhancedModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = UUIDField(db_index=True)
    order_id = UUIDField(db_index=True)
    invoice = models.CharField(max_length=100, default="")

    class Meta:
        db_table = 'invoice'
