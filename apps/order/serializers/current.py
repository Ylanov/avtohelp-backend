from rest_framework import serializers
from django.contrib.gis.geos.point import Point
from order import models


class AssistanceRequestMixin(serializers.ModelSerializer):
    """AssistanceRequest mixin"""

    user_id = serializers.IntegerField(source='user.id')

    class Meta:
        """Meta-class"""

        model = models.AssistanceRequest
        fields = ('id', 'user', 'geo_lat', 'geo_lon')

    def get_geo_lat(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.location, Point):
            return obj.location.y

    def get_geo_lon(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.location, Point):
            return obj.location.x


class AssistanceRequestListSerializer(AssistanceRequestMixin):
    """List of AssistanceRequest objects by user"""
    pass


class AssistanceRequestCreateSerializer(AssistanceRequestMixin):
    """Create object of AssistanceRequest by user"""

    user = serializers.IntegerField(write_only=True)

    class Meta:
        """Meta class"""

        model = models.AssistanceRequest
        fields = ('id', 'user')
