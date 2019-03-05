from django.contrib.gis.geos.point import Point
from rest_framework import serializers

from order import models
from userprofile import models as profile_models


class AssistanceRequestMixin(serializers.ModelSerializer):
    """AssistanceRequest mixin"""

    user_id = serializers.IntegerField(source='user.id')
    geo_lat = serializers.SerializerMethodField()
    geo_lon = serializers.SerializerMethodField()

    class Meta:
        """Meta-class"""

        model = models.AssistanceRequest
        fields = ('id', 'created', 'user', 'geo_lat', 'geo_lon')

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


class CarViewSerializer(serializers.ModelSerializer):
    """Car serializer for Requests"""

    class Meta:
        """Meta class"""
        model = profile_models.Car
        fields = ('id', 'mark', 'model', 'color', 'license_plate')


class ProfileViewSerializer(serializers.ModelSerializer):
    """Profile serializer for Requests"""

    phone = serializers.CharField(source='user.phone.as_e164')
    car = CarViewSerializer(source='user.car_set.first')

    class Meta:
        """Meta class"""

        model = profile_models.Profile
        fields = ('id', 'first_name', 'last_name', 'middle_name',
                  'phone', 'car')


class AssistanceRequestCreateSerializer(serializers.ModelSerializer):
    """Create object of AssistanceRequest by user"""

    # RESPONSE
    profile = ProfileViewSerializer(read_only=True, source='user.profile')
    # COMMON
    # phone = PhoneNumberField(write_only=True, required=False)
    issue = serializers.CharField()
    description = serializers.CharField()
    geo_lat = serializers.FloatField(allow_null=True)
    geo_lon = serializers.FloatField(allow_null=True)

    class Meta:
        """Meta class"""

        model = models.AssistanceRequest
        fields = ('id', 'created', 'profile', 'issue',
                  'description', 'geo_lat', 'geo_lon')

    def validate(self, attrs):
        """Override validate method"""
        # get user from request
        user = self.context.get('request').user
        attrs['user_id'] = user.id
        # get first user car
        attrs['car_id'] = user.car_set.first().id
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

    def create(self, validated_data):
        """Override Create method"""
        return super().create(validated_data)
