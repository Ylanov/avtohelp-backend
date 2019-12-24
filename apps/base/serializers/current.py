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
                  'publish_date', 'recommendation', 'image')
        read_only_fields = ('id', 'image', 'publish')


class RecommendationsListSerializer(serializers.ModelSerializer):
    """Serializer for NewsListView"""

    class Meta:
        """Meta class"""

        model = models.Newsletter
        fields = ('id', 'created', 'title', 'short_description', 
                    'publish_date', 'publish')
        read_only_fields = ('id', 'created', 'title', 'short_description', 
                    'publish_date', 'publish')


class RecommendationCreateSerializer(serializers.ModelSerializer):
    """Serializer for create Newsletter"""

    class Meta:
        """Meta class"""
        model = models.Newsletter
        fields = ('id', 'created', 'title', 'short_description', 
                    'publish_date', 'recommendation', 'image')

    # def validate(self, attrs):
    #     """Override validate method"""
    #     attrs['initiator'] = self.context.get('request').user
    #     attrs['participant'] = attrs.get('participant').user

    #     # Check if participant is not an initiator
    #     if attrs['initiator'] == attrs['participant']:
    #         raise api_exceptions.EqualIDError()

    #     # Check if participant not in black list
    #     are_foes = profile_models.BlackList.objects.are_foes(attrs['initiator'], attrs['participant'])
    #     if are_foes:
    #         raise api_exceptions.AreFoesError(attrs['initiator'], attrs['participant'])

    #     return attrs

    def create(self, validated_data):
        """Override create method"""
        user = self.context['request'].user
        if not user.is_anonymous:
            validated_data['author'] = user
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
