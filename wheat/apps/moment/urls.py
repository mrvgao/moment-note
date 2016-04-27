from customs.urls import get_urlpattern
import apis
urlpatterns = get_urlpattern({
    'moments': apis.MomentViewSet,
}, api_name='moment-api')
