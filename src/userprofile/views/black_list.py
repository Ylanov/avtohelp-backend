from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.generics import get_object_or_404

from ..models import BlackList
from ..serializers import current as serializers
from .mixins import ProfileBlackListMixin


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


class BlackListDestroyView(ProfileBlackListMixin, generics.DestroyAPIView):
    """
    View for destroy blacklist request
    """

    def get_object(self):
        """Override get_object method"""
        return get_object_or_404(
            BlackList.objects.by_profiles(
                owner=self.request.user.profile, foe=self.kwargs.get("profile_id")
            )
        )
