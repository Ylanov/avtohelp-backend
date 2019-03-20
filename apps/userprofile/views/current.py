from fcm_django.models import FCMDevice
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.db.models import Q, Subquery

from userprofile import models, filters
from userprofile.serializers import current as serializers


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
        """Object as resylt and the view is displaying or None."""
        queryset = self.get_queryset()  # get the base queryset
        queryset = self.filter_queryset(queryset)  # apply any filter backends
        # generate filter
        filter = {f: self.request.data.get(f) for f in self.lookup_fields
                  if self.request.data.get(f)}

        # get object and check permissions or return None
        obj = queryset.filter(**filter).first()
        obj and self.check_object_permissions(self.request, obj)
        return obj


# Profile


class ProfileListView(generics.ListAPIView):
    """
    View for list of user profiles
    With filter by fields:
    :param first_name: Search profile by first_name
    :param last_name: Search profile by last_name
    :param middle_name: Search profile by middle_name
    :param license_plate: Search profile by car license plate
    :type first_name: CharField Anatoly
    :type last_name: CharField Feteleu
    :type middle_name: CharField Vyacheslavovich
    :type license_plate: CharField "aaa123бб 70"
    """

    serializer_class = serializers.ProfileListSerializer
    filter_class = filters.ProfileListFilterSet

    def get_queryset(self):
        """Override get_queryset method"""
        return models.Profile.objects.select_related(
            'user'
        ).friendly(self.request.user).order_by('first_name', 'last_name', 'middle_name')


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
        "middle_name": CharField,
        "city_id": IntegerField,
    }
    Response (PATCH): {**user_data}

    Request (PUT):
    {
        "first_name": CharField,
        "last_name": CharField,
        "middle_name": CharField,
        "city_id": IntegerField,
        "avatar": ImagePath
    }
    Response (PUT): {**user_data}

    :return: return object
    """

    serializer_class = serializers.ProfileSerializer
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
        return models.Profile.objects.select_related(
            'user'
        ).friendly(self.request.user)


# Car


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


class ProfileCarDeleteView(generics.DestroyAPIView):
    """
    View for delete profile car
    RESPONSE: None
    :return: None
    """
    queryset = models.ProfileCar.objects.select_related('owner', 'car', 'color', 'car__mark',
                                                        'car__car_model__mark').all()


class ProfileCarDetailView(generics.RetrieveUpdateAPIView):
    """
    View for retrieve profile car
    :return: object
    """
    serializer_class = serializers.ProfileCarCreateSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return models.ProfileCar.objects.select_related('owner', 'car', 'color', 'car__mark',
                                                        'car__car_model__mark').filter(owner=self.request.user)


class ProfileCarListView(generics.ListAPIView):
    """
    View for retrieve profile cars
    :return: object
    """
    serializer_class = serializers.ProfileCarListSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return models.ProfileCar.objects.select_related('owner', 'car', 'color', 'car__mark',
                                                        'car__car_model__mark').filter(owner=self.request.user)


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
    {"user_id": IntegerField}
    RESPONSE:
    {}
    """
    serializer_class = serializers.FriendRequestSerializer
    queryset = models.FriendRequest.objects.select_related('owner', 'owner__profile').all()


class FriendListDestroyView(generics.DestroyAPIView):
    """
    View for destroy friendlist request
    """

    def perform_destroy(self, instance):
        """Override perform_destroy method"""
        instance.request.delete()
        instance.delete()

    def get_queryset(self):
        """Override get queryset method"""
        return models.FriendList.objects.common(user=self.request.user)


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
    queryset = models.FriendRequest.objects.select_related('owner', 'owner__profile').not_approved()

    def get_object(self):
        return models.FriendRequest.objects.get(id=self.kwargs.get('pk'))


class FriendRequestListView(generics.ListAPIView):
    """
    View for request for adding ME to FriendList
    Friend requests FROM ME to adding to my list
    """

    serializer_class = serializers.FriendRequestSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return models.FriendRequest.objects.requests(invited=self.request.user).not_approved()


class OutFriendRequestListView(generics.ListAPIView):
    """
    View for retrieve user friend requests
    My friend requests FOR ADDING SMBD to my list
    """

    serializer_class = serializers.FriendRequestSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return models.FriendRequest.objects.my_requests(owner=self.request.user).not_approved()


class FriendRequestDetailView(generics.RetrieveAPIView):
    """
    View for retrieve user friend request
    """

    serializer_class = serializers.FriendRequestSerializer
    queryset = models.FriendRequest.objects.all()


# Blacklist


class ProfileBlackListView(generics.ListAPIView):
    """
    View for retrieve user blacklist
    """

    serializer_class = serializers.ProfileBlackListSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return models.BlackList.objects.common(user=self.request.user)


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

    def get_queryset(self):
        """Override get queryset method"""
        return models.BlackList.objects.my_list(user=self.request.user)
