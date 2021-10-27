from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from utils.paginations import ProjectCursorPagination

from .. import filters
from ..serializers import current as serializers
from .mixins import ProfileMixin


class ProfileCountView(ProfileMixin, generics.ListAPIView):
    """
    View for counter of user profiles
    """

    def get(self, request, format=None):
        user_count = self.queryset.count()
        content = {"user_count": user_count}
        return Response(content)


class ProfileListView(ProfileMixin, generics.ListAPIView):
    """
    View for list of user profiles
    With filter by fields:
        param online: Search profile by online status
        type online: Boolean True

        param friend: Search profile by friend status
        type friend: Boolean False

        param search:
            Search profile by fields
            - first name
            - last name
            - middle name
            - license plate
        type search: CharField aa000aa 123
    """

    serializer_class = serializers.ProfileListSerializer
    filter_class = filters.ProfileListFilterSet
    pagination_class = ProjectCursorPagination

    def get_queryset(self):
        """Override get_queryset method"""
        return (
            self.queryset.annotate_online_status()
            .annotate_friend_status(self.request.user)
            .valid()
            .friendly(self.request.user)
            .order_by("first_name", "last_name")
            .distinct()
        )


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
        return get_object_or_404(
            self.queryset, pk=self.request.user.profile.pk
        )


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
        return get_object_or_404(
            self.queryset, pk=self.request.user.profile.pk
        )


class ProfileDetailView(ProfileMixin, generics.RetrieveAPIView):
    """
    View for retrieving user profile.
    Allowed HTTP-requests: (GET)
    """

    serializer_class = serializers.ProfileSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return (
            self.queryset.annotate_online_status()
            .annotate_friend_status(self.request.user)
            .annotate_foe_status(self.request.user)
            .annotate_friend_request_status(self.request.user)
            .distinct("id")
        )


class ProfileLocationUpdateView(generics.UpdateAPIView):
    """
    View for updating user profile location.
    Allowed HTTP-requests: (UPDATE)
    """

    serializer_class = serializers.ProfileLocationUpdateSerializer

    def get_object(self):
        """Override get_object method"""
        return self.request.user.profilelocation
