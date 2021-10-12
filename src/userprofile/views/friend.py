from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.generics import get_object_or_404

from .. import filters
from ..models import FriendList, FriendRequest
from ..serializers import current as serializers
from .mixins import FriendRequestMixin


class ProfileFriendListView(generics.ListAPIView):
    """
    View for retrieve user friends
    """

    serializer_class = serializers.ProfileFriendListSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        return FriendList.objects.common(user=self.request.user).exclude(
            friend__profile__first_name__isnull=True
        )


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
        return get_object_or_404(
            FriendList.objects.by_profiles(
                self.request.user.profile, self.kwargs.get("profile_id")
            )
        )


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
        return FriendRequest.objects.common_by_user(user=self.request.user)


class InFriendRequestDeleteView(generics.DestroyAPIView):
    """
    View for delete incoming friend request
    """

    def get_queryset(self):
        """Override get_queryset method"""
        return FriendRequest.objects.common_by_user(
            user=self.request.user
        ).not_approved()
