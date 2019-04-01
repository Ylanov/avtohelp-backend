"""Version 1.0.0 url conf."""
from django.urls import path

from userprofile.views import current as views

app_name = 'userprofile'

urlpatterns = [
    path('device', views.FCMDeviceViewSet.as_view(),
         name='device'),

    # Profiles
    path('profiles', views.ProfileListView.as_view(),
         name='profile-list'),

    path('profiles/<int:pk>', views.ProfileDetailView.as_view(),
         name='profile-detail'),

    path('profile/detail', views.MyProfileDetailView.as_view(),
         name='my-profile-detail'),

    # Profile car
    path('profile/cars', views.ProfileCarListView.as_view(),
         name='profile-car-list'),

    path('profile/cars/<int:pk>', views.ProfileCarDetailView.as_view(),
         name='profile-car-detail'),

    path('profile/cars/add', views.ProfileCarCreateView.as_view(),
         name='profile-car-create'),

    path('profile/cars/delete/<int:pk>', views.ProfileCarDeleteView.as_view(),
         name='profile-car-delete'),

    # Profile gallery
    path('profile/gallery', views.ProfileGalleryListView.as_view(),
         name='profile-gallery-list'),

    path('profile/gallery/<int:pk>', views.ProfileGalleryDetailView.as_view(),
         name='profile-gallery-detail'),

    path('profile/gallery/<int:pk>/set_main', views.ProfileGallerySetMainView.as_view(),
         name='profile-gallery-set_main'),

    path('profile/gallery/add', views.ProfileGalleryCreateView.as_view(),
         name='profile-gallery-create'),

    path('profile/gallery/<int:pk>/delete', views.ProfileGalleryDeleteView.as_view(),
         name='profile-gallery-delete'),

    # Friendlist
    path('profile/friends', views.ProfileFriendListView.as_view(),
         name='friendlist-list'),

    path('profile/friends/add', views.FriendRequestCreateView.as_view(),
         name='friendrequest-create'),

    path('profile/friends/<int:pk>/remove', views.FriendListDestroyView.as_view(),
         name='friendlist-remove'),

    path('profile/friends/requests/incoming', views.InFriendRequestListView.as_view(),
         name='friendrequest-list'),

    path('profile/friends/requests/incoming/<int:pk>', views.FriendRequestDetailView.as_view(),
         name='friendrequest-detail'),

    path('profile/friends/requests/incoming/<int:pk>/approve', views.FriendRequestApproveView.as_view(),
         name='friendrequest-approve'),

    path('profile/friends/requests/outgoing', views.OutFriendRequestListView.as_view(),
         name='my-friendrequest-list'),

    path('profile/friends/requests/outgoing/<int:pk>', views.FriendRequestDetailView.as_view(),
         name='my-friendrequest-detail'),

    path('profile/friends/requests/outgoing/<int:pk>/delete', views.FriendRequestDeleteView.as_view(),
         name='my-friendrequest-delete'),

    # Blacklist
    path('profile/blacklist', views.ProfileBlackListView.as_view(),
         name='blacklistrequest-list'),

    path('profile/blacklist/add', views.BlackListCreateView.as_view(),
         name='blacklistrequest-create'),

    path('profile/blacklist/<int:pk>', views.BlackListDetailView.as_view(),
         name='blacklistrequest-detail'),

    path('profile/blacklist/<int:pk>/delete', views.BlackListDestroyView.as_view(),
         name='blacklistrequest-delete'),
]
