"""Version 1.0.0 url conf."""
from django.urls import path

from userprofile.views import current as views

app_name = 'userprofile'

urlpatterns = [
    path('device', views.FCMDeviceViewSet.as_view(), name='device'),
    path('profiles', views.ProfileListView.as_view(), name='profile-list'),
    path('profile/detail', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('profile/friends', views.ProfileFriendListView.as_view(), name='friendlist-list'),
    path('profile/friends/add', views.FriendRequestCreateView.as_view(), name='friendrequest-create'),
    path('profile/friends/requests/', views.FriendRequestListView.as_view(), name='friendrequest-list'),
    path('profile/friends/requests/<int:pk>/approve', views.FriendRequestApproveView.as_view(), name='friendrequest-approve'),
    path('profile/friends/requests/my', views.MyFriendRequestListView.as_view(), name='my-friendrequest-list'),
    path('profile/friends/requests/my/<int:pk>', views.FriendRequestDetailView.as_view(), name='my-friendrequest-detail'),
    path('profile/blacklist', views.ProfileBlackListView.as_view(), name='blacklist-list'),
    path('profile/blacklist/add', views.BlackListCreateCreateView.as_view(), name='blacklistrequest-create'),
]
