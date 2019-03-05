from fcm_django.models import FCMDevice
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.db.models import Q, Subquery

from userprofile import models, filters
from userprofile.serializers import current as serializers


# Create your views here.
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


class ProfileListView(generics.ListAPIView):
    """
    View for list of user profiles
    With filter by fields:
    :param first_name: Search profile by first_name
    :param last_name: Search profile by last_name
    :param license_plate: Search profile by car license plate
    :type first_name: CharField Anatoly
    :type last_name: CharField Feteleu
    :type license_plate: CharField "aaa123бб 70"
    """

    pagination_class = None
    serializer_class = serializers.ProfileListSerializer
    filter_class = filters.ProfileListFilterSet
    queryset = models.Profile.objects.all().select_related(
        'friends',
        'blacklist',
        'user',
    ).order_by('first_name', 'last_name')

    def get_queryset(self):
        """Override get_queryset method"""
        user = self.request.user
        return self.queryset.filter(
            # Get all users that are NOT in my BlackList
            ~Q(user__id__in=Subquery(models.BlackList.objects.my_list(user).values('foe__id')))).filter(
            # Get all users in which I can't be blacklisted
            ~Q(user__id__in=Subquery(models.BlackList.objects.in_list(user).values('owner__id')))).filter(
            # Get all users that are NOT in my FriendList
            ~Q(user__id__in=Subquery(models.FriendList.objects.my_list(user).values('friend__id')))).filter(
            # Get all users that are NOT in my FriendList
            ~Q(user__id__in=Subquery(models.FriendList.objects.in_list(user).values('owner__id')))).exclude(user=user)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
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
        

class ProfileFriendListView(generics.ListAPIView):
    """
    View for retrieve user friends
    """

    serializer_class = serializers.ProfileFriendListSerializer
    queryset = models.FriendList.objects.all()

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.my_list(user=self.request.user)


class FriendRequestCreateView(generics.CreateAPIView):
    """
    View for creating friend request
    REQUEST:
    {"user_id": IntegerField}
    RESPONSE:
    {
        "id": IntegerField,
        "created": DateTimeField,
        "user_id": IntegerField,
        "approved": BooleanField
    }
    """
    serializer_class = serializers.FriendRequestSerializer
    queryset = models.FriendRequest.objects.select_related('profile__friendlist', 'user').all()


class ProfileBlackListView(generics.ListAPIView):
    """
    View for retrieve user blacklist
    """

    serializer_class = serializers.ProfileBlackListSerializer
    queryset = models.BlackList.objects.all()

    def get_queryset(self):
        """Override get_queryset method"""
        return self.queryset.my_list(user=self.request.user)


class BlackListRequestCreateView(generics.CreateAPIView):
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
    serializer_class = serializers.BlackListRequestSerializer
    queryset = models.FriendRequest.objects.select_related('profile__blacklist', 'user').all()


class CarListView(generics.ListAPIView):
    """User car list view"""

    serializer_class = serializers.CarListSerializer
    queryset = models.Car.objects.all()
    pagination_class = None


class CarDetailView(generics.RetrieveAPIView):
    """User car detail view"""

    serializer_class = serializers.CarDetailSerializer
    queryset = models.Car.objects.all()
