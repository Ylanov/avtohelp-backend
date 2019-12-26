import datetime
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
                  'publish_date', 'recommendation', 'image', 'refused')
        read_only_fields = ('id', 'image', 'publish', 'refused')


class RecommendationsListSerializer(serializers.ModelSerializer):
    """Serializer for NewsListView"""

    status = serializers.SerializerMethodField()

    class Meta:
        """Meta class"""

        model = models.Newsletter
        fields = ('id', 'created', 'title', 'short_description', 
                    'text', 'publish_date', 'status')
        read_only_fields = ('id', 'created', 'title', 'short_description', 
                    'text', 'publish_date', 'status')

    def get_status(self, obj):
        if obj.refused == True:
            return 'refused'
        if obj.publish == False:
            return 'pending'
        if obj.publish == True:
            return 'published'
        return 'refused'


class RecommendationCreateSerializer(serializers.ModelSerializer):
    """Serializer for create Newsletter"""

    publish_date = serializers.DateTimeField(required=False)

    class Meta:
        """Meta class"""
        model = models.Newsletter
        fields = ('id', 'created', 'title', 'short_description', 
                    'text', 'publish_date', 'recommendation', 'image')

    def create(self, validated_data):
        """Override create method"""
        user = self.context['request'].user
        if not user.is_anonymous:
            validated_data['author'] = user
        validated_data['recommendation'] = True
        validated_data['publish_date'] = datetime.datetime.now()
        news = models.Newsletter.objects.create(**validated_data)
        return news



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
