from rest_framework import generics

from ..models import BlackList, FriendRequest, Profile, ProfileCar, ProfileGallery


class ProfileMixin:
    """Profile mixin"""

    queryset = Profile.objects.select_related("user")


class ProfileBlackListMixin:
    """ProfileBlackLists mixin"""

    queryset = BlackList.objects.select_related("owner__profile", "foe__profile")


class ProfileCarMixin:
    """ProfileCar mixin"""

    queryset = ProfileCar.objects.select_related(
        "owner", "car", "color", "car__mark", "car__car_model__mark"
    )


class MyProfileCarMixin(ProfileCarMixin):
    """Mixin for model ProfileCar"""

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.filter(owner=self.request.user)


class ProfileGalleryMixin:
    """ProfileGallery mixin"""

    queryset = ProfileGallery.objects.select_related("profile")


class MyProfileGalleryMixin(ProfileGalleryMixin, generics.GenericAPIView):
    """Mixin for ProfileGallery views"""

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.filter(profile__user=self.request.user)


class FriendRequestMixin:
    """FriendRequest mixin"""

    queryset = FriendRequest.objects.select_related(
        "owner__profile", "invited__profile"
    )
