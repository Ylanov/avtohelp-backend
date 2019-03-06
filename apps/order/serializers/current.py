from django.contrib.gis.geos.point import Point
from rest_framework import serializers

from order import models
from userprofile.serializers import current as profile_serializers


class AssistanceRequestMixin(serializers.ModelSerializer):
    """AssistanceRequest mixin"""

    geo_lat = serializers.SerializerMethodField()
    geo_lon = serializers.SerializerMethodField()

    class Meta:
        """Meta-class"""

        model = models.AssistanceRequest
        fields = ('id', 'created', 'geo_lat', 'geo_lon')

    def get_geo_lat(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.user.profilelocation.location, Point):
            return obj.user.profilelocation.location.y

    def get_geo_lon(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.user.profilelocation.location, Point):
            return obj.user.profilelocation.location.x


class AssistanceRequestListSerializer(AssistanceRequestMixin):
    """List of AssistanceRequest objects by user"""

    class Meta:
        """Meta class"""
        model = models.AssistanceRequest
        fields = ('id', 'created', 'user', 'issue', 'description', 'geo_lat', 'geo_lon')


class AssistanceRequestCreateSerializer(serializers.ModelSerializer):
    """Create object of AssistanceRequest by user"""

    # RESPONSE
    profile = profile_serializers.ProfileViewSerializer(read_only=True, source='user.profile')

    # REQUEST
    geo_lat = serializers.FloatField(allow_null=True)
    geo_lon = serializers.FloatField(allow_null=True)

    class Meta:
        """Meta class"""

        model = models.AssistanceRequest
        fields = ('id', 'created', 'issue', 'description',
                  'geo_lat', 'geo_lon', 'profile', )

    def validate(self, attrs):
        """Override validate method"""
        # get user from request
        user = self.context.get('request').user
        attrs['user_id'] = user.id
        # if geo_lat and geo_lon was sent
        geo_lat = attrs.pop('geo_lat') if 'geo_lat' in attrs else None
        geo_lon = attrs.pop('geo_lon') if 'geo_lon' in attrs else None
        if geo_lat and geo_lon:
            # Point(longitude, latitude)
            attrs['location'] = Point(geo_lon, geo_lat)
        return attrs

    def to_representation(self, instance):
        """Override to_representation method"""
        if instance.location and isinstance(instance.location, Point):
            # Point(longitude, latitude)
            setattr(instance, 'geo_lat', instance.location.y)
            setattr(instance, 'geo_lon', instance.location.x)
        else:
            setattr(instance, 'geo_lat', float(0))
            setattr(instance, 'geo_lon', float(0))
        return super().to_representation(instance)

