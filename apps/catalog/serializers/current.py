"""Catalogue app serializers."""
from rest_framework import serializers

from catalog import models


class CityListSerializer(serializers.ModelSerializer):
    """City list serializer"""

    class Meta:
        """Meta model"""

        model = models.City
        fields = ('id', 'created', 'name')


class CityDetailSerializer(serializers.ModelSerializer):
    """City detail serializer"""

    class Meta:
        """Meta model"""

        model = models.City
        fields = ('id', 'created', 'name')
