from django.urls import path

from .views import *

app_name = "userprofile"

urlpatterns = [
    path("device", FCMDeviceViewSet.as_view(), name="device"),
    # Profiles
    path("profiles", ProfileListView.as_view(), name="profile-list"),
    path("profiles/<int:pk>", ProfileDetailView.as_view(), name="profile-detail"),
    path("profile/detail", MyProfileDetailView.as_view(), name="my-profile-detail"),
    path(
        "profile/change_avatar",
        ProfileChangeAvatarView.as_view(),
        name="change-profile-avatar",
    ),
    path(
        "profile/update-location",
        ProfileLocationUpdateView.as_view(),
        name="update-profile-location",
    ),
    # Profile car
    path("profile/cars", ProfileCarListView.as_view(), name="profile-car-list"),
    path(
        "profile/cars/<int:pk>",
        ProfileCarDetailView.as_view(),
        name="profile-car-detail",
    ),
    path(
        "profile/cars/add",
        ProfileCarCreateView.as_view(),
        name="profile-car-create",
    ),
    path(
        "profile/cars/delete/<int:pk>",
        ProfileCarDeleteView.as_view(),
        name="profile-car-delete",
    ),
    #   Profile gallery
    path(
        "profile/gallery",
        ProfileGalleryListView.as_view(),
        name="profile-gallery-list",
    ),
    path(
        "profile/gallery/<int:pk>",
        ProfileGalleryDetailView.as_view(),
        name="profile-gallery-detail",
    ),
    path(
        "profile/gallery/add",
        ProfileGalleryCreateView.as_view(),
        name="profile-gallery-create",
    ),
    path(
        "profile/gallery/<int:pk>/delete",
        ProfileGalleryDeleteView.as_view(),
        name="profile-gallery-delete",
    ),
    #   Friend-list
    path("profile/friends", ProfileFriendListView.as_view(), name="friendlist-list"),
    path(
        "profile/friends/add",
        FriendRequestCreateView.as_view(),
        name="friendrequest-create",
    ),
    path(
        "profile/friends/<int:profile_id>/delete",
        FriendListDestroyView.as_view(),
        name="friendlist-delete",
    ),
    path(
        "profile/friends/requests/incoming",
        InFriendRequestListView.as_view(),
        name="friendrequest-list",
    ),
    path(
        "profile/friends/requests/incoming/<int:pk>",
        FriendRequestDetailView.as_view(),
        name="friendrequest-detail",
    ),
    path(
        "profile/friends/requests/incoming/<int:pk>/approve",
        FriendRequestApproveView.as_view(),
        name="friendrequest-approve",
    ),
    path(
        "profile/friends/requests/incoming/<int:pk>/delete",
        InFriendRequestDeleteView.as_view(),
        name="friendrequest-delete",
    ),
    path(
        "profile/friends/requests/outgoing",
        OutFriendRequestListView.as_view(),
        name="my-friendrequest-list",
    ),
    path(
        "profile/friends/requests/outgoing/<int:pk>",
        FriendRequestDetailView.as_view(),
        name="my-friendrequest-detail",
    ),
    path(
        "profile/friends/requests/outgoing/<int:pk>/delete",
        OutFriendRequestDeleteView.as_view(),
        name="my-friendrequest-delete",
    ),
    # Blacklist
    path(
        "profile/blacklist",
        ProfileBlackListView.as_view(),
        name="blacklistrequest-list",
    ),
    path(
        "profile/blacklist/add",
        BlackListCreateView.as_view(),
        name="blacklistrequest-create",
    ),
    path(
        "profile/blacklist/<int:pk>",
        BlackListDetailView.as_view(),
        name="blacklistrequest-detail",
    ),
    path(
        "profile/blacklist/<int:profile_id>/delete",
        BlackListDestroyView.as_view(),
        name="blacklistrequest-delete",
    ),
    # User counter
    path("profiles/count", ProfileCountView.as_view(), name="profile-count"),
]
