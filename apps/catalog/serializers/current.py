"""Catalogue app serializers."""
from rest_framework import serializers

from catalog import models


class CarListSerializer(serializers.ModelSerializer):
    """Car list serialzier"""

    class Meta:
        """Meta model"""

        model = models.Car
        fields = ('id', 'created', 'user')


class CarDetailSerializer(serializers.ModelSerializer):
    """Car detail serialzier"""

    class Meta:
        """Meta model"""

        model = models.Car
        fields = ('id', 'created', 'modified', 'user', 'mark',
                  'model', 'color', 'license_plate')


class CarMarkListSerializer(serializers.ModelSerializer):
    """Car brand list serializer"""

    class Meta:
        """Meta model"""

        model = models.CarMark
        fields = ('id', 'created', 'name')


class CarMarkDetailSerializer(serializers.ModelSerializer):
    """Car brand detail serializer"""

    class Meta:
        """Meta model"""

        model = models.CarMark
        fields = ('id', 'created', 'modified',
                  'name')


class CarModelListSerializer(serializers.ModelSerializer):
    """Car model list serializer"""

    class Meta:
        """Meta model"""

        model = models.CarModel
        fields = ('id', 'created', 'name')


class CarModelDetailSerializer(serializers.ModelSerializer):
    """Car model detail serializer"""

    class Meta:
        """Meta model"""

        model = models.CarModel
        fields = ('id', 'created', 'modified',
                  'name', 'mark')


class CarColorListSerializer(serializers.ModelSerializer):
    """Car color list serializer"""

    class Meta:
        """Meta model"""

        model = models.CarColor
        fields = ('id', 'created', 'name')


class CarColorDetailSerializer(serializers.ModelSerializer):
    """Car color detail serializer"""

    class Meta:
        """Meta model"""

        model = models.CarColor
        fields = ('id', 'created', 'modified',
                  'name')


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
        fields = ('id', 'created', 'modified',
                  'name')


class ServiceListSerializer(serializers.ModelSerializer):
    """Service list serializer"""

    class Meta:
        """Meta model"""

        model = models.Service
        fields = ('id', 'created', 'name')


class ServiceDetailSerializer(serializers.ModelSerializer):
    """Service detail serializer"""

    class Meta:
        """Meta model"""

        model = models.Service
        fields = ('id', 'created', 'modified', 'name',
                  'category', 'description', 'location',
                  'phone')
