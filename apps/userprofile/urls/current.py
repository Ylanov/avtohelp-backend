"""Version 1.0.0 url conf."""
from django.urls import path

from userprofile.views import current as views

app_name = 'userprofile'

urlpatterns = [
    path('device', views.FCMDeviceViewSet.as_view(),
         name='device'),

    path('profiles', views.ProfileListView.as_view(),
         name='profile-list'),

    path('profiles/<int:pk>', views.ProfileDetailView.as_view(),
         name='profile-detail'),

    path('profile/detail', views.MyProfileDetailView.as_view(),
         name='my-profile-detail'),

    path('profile/cars', views.ProfileCarListView.as_view(),
         name='profile-car-list'),

    path('profile/cars/<int:pk>', views.ProfileCarDetailView.as_view(),
         name='profile-car-detail'),

    path('profile/cars/add', views.ProfileCarCreateView.as_view(),
         name='profile-car-create'),

    path('profile/cars/delete/<int:pk>', views.ProfileCarDeleteView.as_view(),
         name='profile-car-delete'),

    path('profile/friends', views.ProfileFriendListView.as_view(),
         name='friendlist-list'),

    path('profile/friends/add', views.FriendRequestCreateView.as_view(),
         name='friendrequest-create'),

    path('profile/friends/<int:pk>/remove', views.FriendListDestroyView.as_view(),
         name='friendlist-remove'),

    path('profile/friends/requests/incoming', views.FriendRequestListView.as_view(),
         name='friendrequest-list'),

    path('profile/friends/requests/incoming/<int:pk>', views.FriendRequestDetailView.as_view(),
         name='friendrequest-detail'),

    path('profile/friends/requests/incoming/<int:pk>/approve', views.FriendRequestApproveView.as_view(),
         name='friendrequest-approve'),

    path('profile/friends/requests/outgoing', views.OutFriendRequestListView.as_view(),
         name='my-friendrequest-list'),

    path('profile/friends/requests/outgoing/<int:pk>', views.FriendRequestDetailView.as_view(),
         name='my-friendrequest-detail'),

    path('profile/blacklist', views.ProfileBlackListView.as_view(),
         name='blacklistrequest-list'),

    path('profile/blacklist/add', views.BlackListCreateView.as_view(),
         name='blacklistrequest-create'),

    path('profile/blacklist/<int:pk>', views.BlackListDetailView.as_view(),
         name='blacklistrequest-detail'),

    path('profile/blacklist/<int:pk>/remove', views.BlackListDestroyView.as_view(),
         name='blacklistrequest-remove'),
]
