from customs.urls import get_urlpattern
import apis

urlpatterns = get_urlpattern({
#    'groups': apis.GroupViewSet,
    'invitations': apis.InvitationViewSet,
#    'friend': apis.FriendViewSet,
}, api_name='relation-api')
