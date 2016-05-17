from customs.urls import get_urlpattern
from . import apis

urlpatterns = get_urlpattern({
    'invoice': apis.InvoiceViewSet,
    'order': apis.OrderViewSet,
    'address': apis.AddressViewSet,
    'price': apis.PriceViewSet,
    'delivery': apis.DeliveryViewSet,
}, api_name='order-api')
