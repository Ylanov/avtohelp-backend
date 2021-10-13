from rest_framework import generics

from .. import filters
from ..serializers import current as serializers
from .mixins import (
    MyProfileGalleryMixin,
    ProfileGalleryMixin,
)


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
