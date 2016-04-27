from customs.urls import get_urlpattern
import apis
urlpatterns = get_urlpattern({
    'images': apis.ImageViewSet,
}, api_name='image-api')
