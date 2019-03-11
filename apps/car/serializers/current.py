from rest_framework import serializers
from car import models
from django.contrib.gis.geos.point import Point


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


# class CarDetailSerializer(serializers.ModelSerializer):
#     """Car detail serializer"""
#
#     mark = CarMarkDetailSerializer()
#     car_model = CarModelDetailSerializer()
#     color = CarColorDetailSerializer()
#
#     class Meta:
#         """Meta model"""
#
#         model = models.Car
#         fields = ('id', 'created', 'modified', 'license_plate',
#                   'mark', 'car_model', 'color')


class CarDetailSerializer(serializers.ModelSerializer):
    """Car detail serializer"""

    mark_name = serializers.CharField(source='mark.name')
    model_name = serializers.CharField(source='car_model.name')

    class Meta:
        """Meta model"""

        model = models.Car
        fields = ('id', 'created', 'mark_name', 'model_name')



# NOTE: user utils.serializers.CoordinatesSerializer
class ServiceListSerializer(serializers.ModelSerializer):
    """Service list serializer"""

    geo_lat = serializers.SerializerMethodField()
    geo_lon = serializers.SerializerMethodField()

    class Meta:
        """Meta model"""

        model = models.CarService
        fields = ('id', 'created', 'name', 'geo_lat', 'geo_lon')

    def get_geo_lat(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.location, Point):
            return obj.location.y

    def get_geo_lon(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.location, Point):
            return obj.location.x


# NOTE: user utils.serializers.CoordinatesSerializer
class ServiceDetailSerializer(serializers.ModelSerializer):
    """Service detail serializer"""

    geo_lat = serializers.SerializerMethodField()
    geo_lon = serializers.SerializerMethodField()

    class Meta:
        """Meta model"""

        model = models.CarService
        fields = ('id', 'created', 'modified', 'name',
                  'category', 'description', 'geo_lat',
                  'geo_lon', 'phone')

    def get_geo_lat(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.location, Point):
            return obj.location.y

    def get_geo_lon(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.location, Point):
            return obj.location.x


