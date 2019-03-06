from rest_framework import serializers
from base import models


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
