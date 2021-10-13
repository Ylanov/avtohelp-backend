from rest_framework import generics

from ..serializers import current as serializers
from .mixins import (
    MyProfileCarMixin,
    ProfileCarMixin,
)


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
