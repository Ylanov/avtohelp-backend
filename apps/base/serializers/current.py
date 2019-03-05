from rest_framework import serializers
from base import models
from django.contrib.gis.geos.point import Point


class NewsListSerializer(serializers.ModelSerializer):
    """Serializer for NewsListView"""

    class Meta:
        """Meta class"""

        model = models.Newsletter
        fields = ('id', 'created', 'title', 'publish_date', 'text')


class NewsDetailSerializer(serializers.ModelSerializer):
    """Serializer for NewsDetailView"""

    class Meta:
        """Meta class"""

        model = models.Newsletter
        fields = ('id', 'created', 'modified', 'title',
                  'text', 'publish', 'publish_date')


class ServiceListSerializer(serializers.ModelSerializer):
    """Service list serializer"""

    geo_lat = serializers.SerializerMethodField()
    geo_lon = serializers.SerializerMethodField()

    class Meta:
        """Meta model"""

        model = models.Service
        fields = ('id', 'created', 'name', 'geo_lat', 'geo_lon')

    def get_geo_lat(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.location, Point):
            return obj.location.y

    def get_geo_lon(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.location, Point):
            return obj.location.x


class ServiceDetailSerializer(serializers.ModelSerializer):
    """Service detail serializer"""

    geo_lat = serializers.SerializerMethodField()
    geo_lon = serializers.SerializerMethodField()

    class Meta:
        """Meta model"""

        model = models.Service
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


class NotificationListSerializer(serializers.ModelSerializer):
    """Notification list serializer"""

    class Meta:
        """Meta class"""

        model = models.PushNotification
        fields = ('id', 'created', 'user',
                  'event', 'status', 'sent_count')


class NotificationDetailSerializer(serializers.ModelSerializer):
    """Notification list serializer"""

    class Meta:
        """Meta class"""

        model = models.PushNotification
        fields = ('id', 'created', 'user',
                  'title', 'description', 'event',
                  'sent_count', 'status')
