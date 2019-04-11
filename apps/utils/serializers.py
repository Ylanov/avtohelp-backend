from rest_framework import serializers
from django.contrib.gis.geos.point import Point


class CoordinatesSerializer(serializers.Serializer):
    """
    Added additional fields for show geo position in X, Y coord.
    For catalog models
    """
    geo_lat = serializers.SerializerMethodField()
    geo_lon = serializers.SerializerMethodField()

    def get_geo_lat(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.location, Point):
            return obj.location.y

    def get_geo_lon(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.location, Point):
            return obj.location.x


class GeoPositonMixin(serializers.Serializer):
    """
    Added additional fields for show geo position in X, Y coord.
    For profile models
    """

    geo_lat = serializers.SerializerMethodField(read_only=True, allow_null=True)
    geo_lon = serializers.SerializerMethodField(read_only=True, allow_null=True)

    def get_geo_lat(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.user.profilelocation.location, Point):
            return obj.user.profilelocation.location.x

    def get_geo_lon(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.user.profilelocation.location, Point):
            return obj.user.profilelocation.location.y
