from rest_framework import serializers


class CoordinatesSerializer(serializers.Serializer):

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
