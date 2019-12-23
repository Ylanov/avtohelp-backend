from rest_framework import serializers
from base import models


class NewsListSerializer(serializers.ModelSerializer):
    """Serializer for NewsListView"""

    class Meta:
        """Meta class"""

        model = models.Newsletter
        fields = ('id', 'created', 'title', 'short_description', 'publish_date')


class NewsDetailSerializer(serializers.ModelSerializer):
    """Serializer for NewsDetailView"""

    image = serializers.ImageField(source='get_image', required=False)

    class Meta:
        """Meta class"""

        model = models.Newsletter
        fields = ('id', 'created', 'modified', 'title',
                  'short_description', 'text', 'publish',
                  'publish_date', 'image')
        read_only_fields = ('id', 'image', 'publish')


class PushNotificationScheduleSerializer(serializers.ModelSerializer):
    """Serializer for PushNotificationSchedule model"""

    hours = serializers.IntegerField(source='time.hour')
    minutes = serializers.IntegerField(source='time.minute')

    class Meta:
        """Meta class"""
        model = models.PushNotificationSchedule
        fields = ('hours', 'minutes')


class PushNotificationConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for PushNotificationConfiguration model"""

    schedule = PushNotificationScheduleSerializer(many=True, source='notification_schedule')

    class Meta:
        """Meta class"""

        model = models.PushNotificationConfiguration
        fields = ('radius', 'geo_position_lifetime', 'schedule')


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
