from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from userprofile import models, filters
from userprofile.models import FCMDevice
from userprofile.serializers import current as serializers
from utils.paginations import CustomCursorPagination


class FCMDeviceViewSet(generics.GenericAPIView):
    """FCMDevice registration view.

    * Pair of fields **registration_id** and **type** should be unique.
    * In case of requested device existance, existing device will be returned
      instead of creating new one.
    """

    serializer_class = serializers.FCMDeviceSerializer
    lookup_fields = ('registration_id', 'type',)
    queryset = FCMDevice.objects.all()

    def post(self, request, *args, **kwargs):
        """Override post method."""
        instance = self.get_object_or_none()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK if instance else status.HTTP_201_CREATED)

    def get_object_or_none(self):
        """Object as result and the view is displaying or None."""
        queryset = self.get_queryset()  # get the base queryset
        queryset = self.filter_queryset(queryset)  # apply any filter backends
        # generate filter
        filter_params = {f: self.request.data.get(f) for f in self.lookup_fields
                         if self.request.data.get(f)}

        # get object and check permissions or return None
        obj = queryset.filter(**filter_params).first()
        obj and self.check_object_permissions(self.request, obj)
        return obj


# Profile


class ProfileMixin:
    """Profile mixin"""

    queryset = models.Profile.objects.select_related('user')


class ProfileListView(ProfileMixin, generics.ListAPIView):
    """
    View for list of user profiles
    With filter by fields:
        param online: Search profile by online status
        type online: Boolean True

        param friend: Search profile by friend status
        type friend: Boolean False

        param search: Search profile by fields - first name, last name, middle name, license plate
        type search: CharField aa000aa 123
    """

    serializer_class = serializers.ProfileListSerializer
    filter_class = filters.ProfileListFilterSet
    pagination_class = CustomCursorPagination

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.annotate_online_status()\
                            .annotate_friend_status(self.request.user)\
                            .friendly(self.request.user)\
                            .valid()\
                            .order_by('first_name', 'last_name')\
                            .distinct()


class MyProfileDetailView(ProfileMixin, generics.RetrieveUpdateAPIView):
    """
    View for retrieving or update user profile.
    Allowed HTTP-requests: (GET, PATCH, PUT)

    Request (GET): {}
    Response (GET): {**user_data}

    Request (PATCH - partial):
    {
        "first_name": CharField,
        "last_name": CharField,
        "city_id": IntegerField,
    }
    Response (PATCH): {**user_data}

    Request (PUT):
    {
        "first_name": CharField,
        "last_name": CharField,
        "city_id": IntegerField,
    }
    Response (PUT): {**user_data}

    :return: return object
    """

    serializer_class = serializers.MyProfileSerializer

    def get_object(self):
        """Override get object method"""
        return get_object_or_404(self.queryset, pk=self.request.user.profile.pk)


class ProfileChangeAvatarView(ProfileMixin, generics.UpdateAPIView):
    """
    View for retrieving or update user profile.
    Allowed HTTP-requests: (PATCH, PUT)

    Request (PATCH - partial):
    {
        "avatar": ImageField,
    }
    Response (PATCH): {"avatar": "url"}

    Request (PUT - full):
    {
        "avatar": ImageField,
    }
    Response (PUT): {"avatar": "url"}

    :return: return object
    """

    serializer_class = serializers.ProfileChangeAvatar

    def get_object(self):
        """Override get object method"""
        return get_object_or_404(self.queryset, pk=self.request.user.profile.pk)


class ProfileDetailView(ProfileMixin, generics.RetrieveAPIView):
    """
    View for retrieving user profile.
    Allowed HTTP-requests: (GET)
    """

    serializer_class = serializers.ProfileSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.annotate_online_status()\
                            .annotate_friend_status(self.request.user)\
                            .annotate_foe_status(self.request.user)\
                            .annotate_friend_request_status(self.request.user)\
                            .distinct()


class ProfileLocationUpdateView(generics.UpdateAPIView):
    """
    View for updating user profile location.
    Allowed HTTP-requests: (UPDATE)
    """

    serializer_class = serializers.ProfileLocationUpdateSerializer

    def get_object(self):
        """Override get_object method"""
        return self.request.user.profilelocation

# Car


class ProfileCarMixin:
    """ProfileCar mixin"""

    queryset = models.ProfileCar.objects.select_related('owner', 'car', 'color',
                                                        'car__mark', 'car__car_model__mark')


class MyProfileCarMixin(ProfileCarMixin):
    """Mixin for model ProfileCar"""

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.filter(owner=self.request.user)


class ProfileCarCreateView(ProfileCarMixin, generics.CreateAPIView):
    """
    View for creating profile car
    REQUEST:
    {
        "car_model": PrimaryKeyRelatedField,
        "mark": PrimaryKeyRelatedField,
        "color": PrimaryKeyRelatedField,
        "license_plate": CharField
    }
    RESPONSE: object
    :return: object
    """
    serializer_class = serializers.ProfileCarCreateSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset


class ProfileCarDeleteView(MyProfileCarMixin, generics.DestroyAPIView):
    """
    View for delete profile car
    RESPONSE: None
    :return: None
    """


class ProfileCarDetailView(MyProfileCarMixin, generics.RetrieveUpdateAPIView):
    """
    View for retrieve profile car
    :return: object
    """
    serializer_class = serializers.ProfileCarCreateSerializer


class ProfileCarListView(MyProfileCarMixin, generics.ListAPIView):
    """
    View for retrieve profile cars
    :return: object
    """
    serializer_class = serializers.ProfileCarListSerializer


# Gallery


class ProfileGalleryMixin:
    """ProfileGallery mixin"""

    queryset = models.ProfileGallery.objects.select_related('profile')


class MyProfileGalleryMixin(ProfileGalleryMixin, generics.GenericAPIView):
    """Mixin for ProfileGallery views"""

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.filter(profile__user=self.request.user)


class ProfileGalleryCreateView(ProfileGalleryMixin, generics.CreateAPIView):
    """
    View for creating profile gallery
    REQUEST:
    {
        "car_model": PrimaryKeyRelatedField,
        "mark": PrimaryKeyRelatedField,
        "color": PrimaryKeyRelatedField,
        "license_plate": CharField
    }
    RESPONSE: object
    :return: object
    """
    serializer_class = serializers.ProfileGalleryCreateSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset


class ProfileGalleryDeleteView(MyProfileGalleryMixin, generics.DestroyAPIView):
    """
    View for delete profile gallery
    RESPONSE: None
    :return: None
    """


class ProfileGalleryDetailView(ProfileGalleryMixin, generics.RetrieveAPIView):
    """
    View for retrieve profile gallery
    :return: object
    """
    serializer_class = serializers.ProfileGalleryDetailSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset


class ProfileGalleryListView(ProfileGalleryMixin, generics.ListAPIView):
    """
    View for retrieve profile gallery
    :return: object
    """
    serializer_class = serializers.ProfileGalleryListSerializer
    filter_class = filters.ProfileGalleryListFilterSet

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset


# FriendList


class FriendRequestMixin:
    """FriendRequest mixin"""

    queryset = models.FriendRequest.objects.select_related('owner__profile', 'invited__profile')


class ProfileFriendListView(generics.ListAPIView):
    """
    View for retrieve user friends
    """

    serializer_class = serializers.ProfileFriendListSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return models.FriendList.objects.common(user=self.request.user)


class FriendRequestCreateView(FriendRequestMixin, generics.CreateAPIView):
    """
    View for creating friend request
    REQUEST:
    {"profile": IntegerField}
    RESPONSE:
    object
    """
    serializer_class = serializers.FriendRequestCreateSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset


class FriendListDestroyView(generics.DestroyAPIView):
    """
    View for destroy friendlist request
    """

    def perform_destroy(self, instance):
        """Override perform_destroy method"""
        instance.request.delete()
        instance.delete()

    def get_object(self):
        """Override get_object method"""
        return get_object_or_404(models.FriendList.objects.by_profiles(
            self.request.user.profile, self.kwargs.get('profile_id')))


class FriendRequestApproveView(FriendRequestMixin, generics.UpdateAPIView):
    """
    View for approve request from user
    REQUEST:
    {"request": IntegerField}
    RESPONSE:
    {
        "approved": BooleanField
    }
    """
    serializer_class = serializers.FriendRequestApproveSerializer

    def get_queryset(self):
        return self.queryset.to_me(invited=self.request.user).not_approved()


class InFriendRequestListView(FriendRequestMixin, generics.ListAPIView):
    """
    View for request for adding ME to FriendList
    Friend requests FROM ME to adding to my list
    """

    serializer_class = serializers.FriendRequestSerializer
    filter_class = filters.IncomingRequestFilterSet

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.to_me(invited=self.request.user).not_approved()


class OutFriendRequestListView(FriendRequestMixin, generics.ListAPIView):
    """
    View for retrieve user friend requests
    My friend requests FOR ADDING SMBD to my list
    """

    serializer_class = serializers.FriendRequestSerializer
    filter_class = filters.OutgoingRequestFilterSet

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.from_me(owner=self.request.user).not_approved()


class FriendRequestDetailView(FriendRequestMixin, generics.RetrieveAPIView):
    """
    View for retrieve user friend request
    """

    serializer_class = serializers.FriendRequestSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset


class OutFriendRequestDeleteView(generics.DestroyAPIView):
    """
    View for delete outgoing friend request
    """

    def get_queryset(self):
        """Override get queryset method"""
        return models.FriendRequest.objects.common_by_user(user=self.request.user)


class InFriendRequestDeleteView(generics.DestroyAPIView):
    """
    View for delete incoming friend request
    """
    def get_queryset(self):
        """Override get_queryset method"""
        return models.FriendRequest.objects.common_by_user(user=self.request.user).not_approved()


# Blacklist


class ProfileBlackListMixin:
    """ProfileBlackLists mixin"""

    queryset = models.BlackList.objects.select_related('owner__profile', 'foe__profile')


class ProfileBlackListView(ProfileBlackListMixin, generics.ListAPIView):
    """
    View for retrieve user blacklist
    """

    serializer_class = serializers.BlackListDetailSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.my_list(user=self.request.user)


class BlackListCreateView(ProfileBlackListMixin, generics.CreateAPIView):
    """
    View for creating request to add to the blacklist
    REQUEST:
    {"user_id": IntegerField}
    RESPONSE:
    {
        "id": IntegerField,
        "created": DateTimeField,
        "user_id": IntegerField
    }
    """
    serializer_class = serializers.BlackListCreateSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset


class BlackListDetailView(ProfileBlackListMixin, generics.RetrieveAPIView):
    """
    Retrieve view blacklist object
    """
    serializer_class = serializers.BlackListDetailSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset


class BlackListDestroyView(generics.DestroyAPIView):
    """
    View for destroy blacklist request
    """
    def get_object(self):
        """Override get_object method"""
        return get_object_or_404(models.BlackList.objects.by_profiles(
            owner=self.request.user.profile, foe=self.kwargs.get('profile_id')))
