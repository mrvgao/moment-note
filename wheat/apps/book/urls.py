from django.conf.urls import url, include
try:
    from collections import OrderedDict
except:
    from django.utils.datastructures import SortedDict as OrderedDict

import apis
from rest_framework.routers import DefaultRouter
from settings import API_VERSION

# Create a router and register our viewsets with it.
author_router = DefaultRouter()
author_router.register(r'author', apis.AuthorViewSet)

order_router = DefaultRouter()
order_router.register(r'order', apis.OrderViewSet)


book_router = DefaultRouter()
book_router.register(r'book', apis.BookViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browseable API.
urlpatterns = []
urlpattern_dict = OrderedDict({
    'author-api': url(r'^api/%s/' % API_VERSION,
                      include(author_router.urls), name='author_router'),
    'order-api': url(r'^api/%s/' % API_VERSION,
                     include(order_router.urls), name='order_router'),
    'book-api': url(r'^api/%s/' % API_VERSION,
                     include(book_router.urls), name='book_router'),

})

for name, urlpattern in urlpattern_dict.items():
    urlpatterns.append(urlpattern)
