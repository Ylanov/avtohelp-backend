from django.contrib.gis.geos.point import Point
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from order import models
from userprofile.serializers import current as profile_serializers
from utils.serializers import GeoLocationSerializerMixin


class AssistanceRequestListSerializer(
    GeoLocationSerializerMixin, serializers.ModelSerializer
):
    """List of AssistanceRequest objects by user"""

    profile_id = serializers.IntegerField(source="user.profile.id")
    distance = serializers.SerializerMethodField()
    is_owner = serializers.BooleanField()

    class Meta:
        """Meta class"""

        model = models.AssistanceRequest
        fields = (
            "id",
            "created",
            "profile_id",
            "issue",
            "description",
            "geo_lat",
            "geo_lon",
            "distance",
            "is_owner",
        )

    def get_distance(self, obj):
        """Get distance in meters"""
        return obj.distance.m if hasattr(obj, "distance") else None


class AssistanceRequestCreateSerializer(serializers.ModelSerializer):
    """Create object of AssistanceRequest by user"""

    # RESPONSE
    profile = profile_serializers.ProfileViewSerializer(
        read_only=True, source="user.profile"
    )
    distance = serializers.SerializerMethodField()
    is_owner = serializers.BooleanField(read_only=True)

    # REQUEST
    geo_lat = serializers.FloatField(allow_null=True)
    geo_lon = serializers.FloatField(allow_null=True)
    contact_phone = PhoneNumberField(allow_blank=False)
    text_address = serializers.CharField(allow_blank=False)

    class Meta:
        """Meta class"""

        model = models.AssistanceRequest
        fields = (
            "id",
            "created",
            "issue",
            "description",
            "image",
            "geo_lat",
            "geo_lon",
            "profile",
            "contact_phone",
            "text_address",
            "distance",
            "is_owner",
        )

    def validate(self, attrs):
        """Override validate method"""
        # get user from request
        user = self.context.get("request").user
        attrs["user_id"] = user.id
        # if geo_lat and geo_lon was sent
        geo_lat = attrs.pop("geo_lat") if "geo_lat" in attrs else None
        geo_lon = attrs.pop("geo_lon") if "geo_lon" in attrs else None
        if geo_lat and geo_lon:
            # Point(longitude, latitude)
            attrs["location"] = Point(geo_lat, geo_lon)
        return attrs

    def to_representation(self, instance):
        """Override to_representation method"""
        if instance.location and isinstance(instance.location, Point):
            # Point(longitude, latitude)
            setattr(instance, "geo_lat", instance.location.x)
            setattr(instance, "geo_lon", instance.location.y)
        else:
            setattr(instance, "geo_lat", float(0))
            setattr(instance, "geo_lon", float(0))
        return super().to_representation(instance)

    def get_distance(self, obj):
        """Get distance in meters"""
        return obj.distance.m if hasattr(obj, "distance") else None

    def create(self, validated_data):
        """Override create method"""
        return models.AssistanceRequest.objects.make(**validated_data)


class AssistanceRequestUpdateSerializer(serializers.ModelSerializer):
    """Update object of AssistanceRequest by user"""

    status = serializers.ChoiceField(choices=models.AssistanceRequest.STATUS_CHOICES)

    class Meta:
        """Meta class"""

        model = models.AssistanceRequest
        fields = ("status",)
