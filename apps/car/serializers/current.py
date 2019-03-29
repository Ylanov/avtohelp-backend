from rest_framework import serializers
from car import models
from utils.serializers import CoordinatesSerializer


class CarListSerializer(serializers.ModelSerializer):
    """Car list serializer"""

    mark_name = serializers.CharField(source='mark.name')
    model_name = serializers.CharField(source='car_model.name')

    class Meta:
        """Meta model"""

        model = models.Car
        fields = ('id', 'created', 'mark_name', 'model_name')


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
        fields = ('id', 'created', 'name')


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
        fields = ('id', 'created', 'name', 'mark')


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
        fields = ('id', 'created', 'name')


class CarDetailSerializer(serializers.ModelSerializer):
    """Car detail serializer"""

    mark_name = serializers.CharField(source='mark.name')
    model_name = serializers.CharField(source='car_model.name')

    class Meta:
        """Meta model"""

        model = models.Car
        fields = ('id', 'created', 'mark_name', 'model_name')


class ServiceListSerializer(serializers.ModelSerializer, CoordinatesSerializer):
    """Service list serializer"""

    distance = serializers.SerializerMethodField()

    class Meta:
        """Meta model"""

        model = models.CarService
        fields = ('id', 'created', 'name', 'geo_lat', 'geo_lon', 'category', 'distance')

    def get_distance(self, obj):
        """Get distance in meters"""
        return obj.distance.m


class ServiceDetailSerializer(serializers.ModelSerializer, CoordinatesSerializer):
    """Service detail serializer"""

    class Meta:
        """Meta model"""

        model = models.CarService
        fields = ('id', 'created', 'modified', 'name',
                  'category', 'description', 'geo_lat',
                  'geo_lon', 'phone')
