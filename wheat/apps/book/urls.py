import apis
from customs.urls import get_urlpattern

urlpatterns = get_urlpattern({
    'author': apis.AuthorViewSet,
#    'order': apis.OrderViewSet,
    'book': apis.BookViewSet,
}, api_name='book-api')
