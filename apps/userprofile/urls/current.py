"""Version 1.0.0 url conf."""
from django.urls import path

from userprofile.views import current as views

app_name = 'userprofile'

urlpatterns = [
    path('device', views.FCMDeviceViewSet.as_view(), name='device'),
    path('cars', views.CarListView.as_view(), name='car_list'),
    path('cars/<int:pk>', views.CarDetailView.as_view(), name='car-detail'),
    path('profiles', views.ProfileListView.as_view(), name='profile-list'),
    path('profile/detail', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('profile/friends', views.ProfileFriendListView.as_view(), name='friendlist-list'),
    path('profile/friends/request', views.FriendRequestCreateView.as_view(), name='friendrequest-create'),
    path('profile/blacklist', views.ProfileBlackListView.as_view(), name='blacklist-list'),
    path('profile/blacklist/request', views.BlackListRequestCreateView.as_view(), name='blacklistrequest-create'),
]
