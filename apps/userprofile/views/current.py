from django.shortcuts import get_object_or_404
from fcm_django.models import FCMDevice
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from userprofile import models, filters
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


class ProfileListView(generics.ListAPIView):
    """
    View for list of user profiles
    With filter by fields:
    :param online: Search profile by online status
    :param friend: Search profile by friend status
    :param search: Search profile by fields - first name, last name, middle name, license plate
    :type online: Boolean True
    :type friend: Boolean False
    :type search: CharField aa000aa 123
    """

    serializer_class = serializers.ProfileListSerializer
    filter_class = filters.ProfileListFilterSet
    pagination_class = CustomCursorPagination

    def get_queryset(self):
        """Override get_queryset method"""
        return models.Profile.objects.annotate_online_status().annotate_friend_status(
            self.request.user).select_related(
            'user'
        ).friendly(self.request.user).valid().order_by('first_name', 'last_name')


class MyProfileDetailView(generics.RetrieveUpdateAPIView):
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
    queryset = models.Profile.objects.all()

    def get_object(self):
        """Override get object method"""
        return get_object_or_404(self.get_queryset(), pk=self.request.user.profile.pk)


class ProfileChangeAvatarView(generics.UpdateAPIView):
    """
    View for retrieving or update user profile.
    Allowed HTTP-requests: (GET, PATCH, PUT)

    Request (PATCH - partial):
    {
        "avatar": ImageField,
    }
    Response (PATCH): {"avatar": "url"}

    Request (PUT - partial):
    {
        "avatar": ImageField,
    }
    Response (PUT): {"avatar": "url"}

    :return: return object
    """

    serializer_class = serializers.ProfileChangeAvatar
    queryset = models.Profile.objects.all()

    def get_object(self):
        """Override get object method"""
        return get_object_or_404(self.get_queryset(), pk=self.request.user.profile.pk)


class ProfileDetailView(generics.RetrieveAPIView):
    """
    View for retrieving user profile.
    Allowed HTTP-requests: (GET)
    """

    serializer_class = serializers.ProfileSerializer
    queryset = models.Profile.objects.all()

    def get_queryset(self):
        """Override get_queryset method"""
        return models.Profile.objects.select_related('user').annotate_online_status().annotate_friend_status(
            self.request.user).annotate_foe_status(
            self.request.user).annotate_friend_request_status(
            self.request.user)


# Car


class ProfileCarViewMixin(object):
    """Mixin for model ProfileCar"""

    def get_queryset(self):
        """Override get_queryset method"""
        return models.ProfileCar.objects.select_related('owner', 'car', 'color', 'car__mark',
                                                        'car__car_model__mark').filter(owner=self.request.user)


class ProfileCarCreateView(generics.CreateAPIView):
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
    queryset = models.ProfileCar.objects.select_related('owner', 'car', 'color', 'car__mark',
                                                        'car__car_model__mark').all()


class ProfileCarDeleteView(ProfileCarViewMixin, generics.DestroyAPIView):
    """
    View for delete profile car
    RESPONSE: None
    :return: None
    """


class ProfileCarDetailView(ProfileCarViewMixin, generics.RetrieveUpdateAPIView):
    """
    View for retrieve profile car
    :return: object
    """
    serializer_class = serializers.ProfileCarCreateSerializer


class ProfileCarListView(ProfileCarViewMixin, generics.ListAPIView):
    """
    View for retrieve profile cars
    :return: object
    """
    serializer_class = serializers.ProfileCarListSerializer


# Gallery


class ProfileGalleryViewMixin(object):
    """Mixin for ProfileGallery views"""

    def get_queryset(self):
        """Override get_queryset method"""
        return models.ProfileGallery.objects.select_related('profile').filter(profile__user=self.request.user)


class ProfileGalleryCreateView(generics.CreateAPIView):
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
    queryset = models.ProfileGallery.objects.select_related('profile').all()


class ProfileGalleryDeleteView(ProfileGalleryViewMixin, generics.DestroyAPIView):
    """
    View for delete profile gallery
    RESPONSE: None
    :return: None
    """

    def get_queryset(self):
        """Override get_queryset method"""
        return models.ProfileGallery.objects.filter(profile__user=self.request.user)


class ProfileGalleryDetailView(ProfileGalleryViewMixin, generics.RetrieveAPIView):
    """
    View for retrieve profile gallery
    :return: object
    """
    serializer_class = serializers.ProfileGalleryDetailSerializer
    queryset = models.ProfileGallery.objects.select_related('profile').all()

    # def get_queryset(self):
    #     """Override get_queryset method"""
    #     return self.queryset.filter(profile__user=self.request.user)


class ProfileGalleryListView(generics.ListAPIView):
    """
    View for retrieve profile gallery
    :return: object
    """
    serializer_class = serializers.ProfileGalleryListSerializer
    queryset = models.ProfileGallery.objects.select_related('profile').all()
    filter_class = filters.ProfileGalleryListFilterSet

    # def get_queryset(self):
    #     """Override get_queryset method"""
    #     return self.queryset.filter(profile__user=self.request.user)


# FriendList


class ProfileFriendListView(generics.ListAPIView):
    """
    View for retrieve user friends
    """

    serializer_class = serializers.ProfileFriendListSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return models.FriendList.objects.common(user=self.request.user)


class FriendRequestCreateView(generics.CreateAPIView):
    """
    View for creating friend request
    REQUEST:
    {"profile": IntegerField}
    RESPONSE:
    object
    """
    serializer_class = serializers.FriendRequestCreateSerializer
    queryset = models.FriendRequest.objects.select_related('owner', 'owner__profile').all()


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


class FriendRequestApproveView(generics.UpdateAPIView):
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
    queryset = models.FriendRequest.objects.select_related('owner', 'owner__profile')

    def get_queryset(self):
        return self.queryset.to_me(invited=self.request.user).not_approved()


class InFriendRequestListView(generics.ListAPIView):
    """
    View for request for adding ME to FriendList
    Friend requests FROM ME to adding to my list
    """

    serializer_class = serializers.FriendRequestSerializer
    filter_class = filters.IncomingRequestFilterSet

    def get_queryset(self):
        """Override get_queryset method"""
        return models.FriendRequest.objects.to_me(invited=self.request.user).not_approved()


class OutFriendRequestListView(generics.ListAPIView):
    """
    View for retrieve user friend requests
    My friend requests FOR ADDING SMBD to my list
    """

    serializer_class = serializers.FriendRequestSerializer
    filter_class = filters.OutgoingRequestFilterSet

    def get_queryset(self):
        """Override get_queryset method"""
        return models.FriendRequest.objects.from_me(owner=self.request.user).not_approved()


class FriendRequestDetailView(generics.RetrieveAPIView):
    """
    View for retrieve user friend request
    """

    serializer_class = serializers.FriendRequestSerializer
    queryset = models.FriendRequest.objects.all()


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


class ProfileBlackListView(generics.ListAPIView):
    """
    View for retrieve user blacklist
    """

    serializer_class = serializers.BlackListDetailSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return models.BlackList.objects.my_list(user=self.request.user)


class BlackListCreateView(generics.CreateAPIView):
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
    queryset = models.BlackList.objects.select_related('owner', 'foe').all()


class BlackListDetailView(generics.RetrieveAPIView):
    """
    Retrieve view blacklist object
    """
    serializer_class = serializers.BlackListDetailSerializer
    queryset = models.BlackList.objects.select_related('owner', 'foe').all()


class BlackListDestroyView(generics.DestroyAPIView):
    """
    View for destroy blacklist request
    """
    def get_object(self):
        """Override get_object method"""
        return get_object_or_404(models.BlackList.objects.by_profiles(
            owner=self.request.user.profile, foe=self.kwargs.get('profile_id')))
