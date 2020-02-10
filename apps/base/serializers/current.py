import datetime
from rest_framework import serializers
from base import models
from image_cropping.utils import get_backend

class NewsListSerializer(serializers.ModelSerializer):
    """Serializer for NewsListView"""

    class Meta:
        """Meta class"""

        model = models.Newsletter
        fields = ('id', 'created', 'title', 'short_description', 'publish_date')


class NewsDetailSerializer(serializers.ModelSerializer):
    """Serializer for NewsDetailView"""

    image = serializers.SerializerMethodField()
    image_resolution = serializers.SerializerMethodField()

    class Meta:
        """Meta class"""

        model = models.Newsletter
        fields = ('id', 'created', 'modified', 'title',
                  'short_description', 'text', 'publish',
                  'publish_date', 'recommendation', 'image','image_resolution', 'refused')
        read_only_fields = ('id', 'image', 'publish', 'refused')

    def get_image(self, news):
        request = self.context.get('request')

        if not news.image:
            return None

        if not news.cropping:
            return request.build_absolute_uri(news.image.url)

        demention = NewsDetailSerializer.get_dementions(news)
        thumbnail_url = get_backend().get_thumbnail_url(
            news.image,
            {
                'size': (demention[0], demention[1]),
                'box': news.cropping,
                'crop': True,
                'detail': True,
            }
        )
        return request.build_absolute_uri(thumbnail_url)


    def get_dementions(news):
        if not news.cropping:
            return [news.image.width, news.image.height]

        demention = [int(x) for x in news.cropping.split(',') if x]
        x = demention[0] - demention[1]
        y = demention[3] - demention[2]

        if x<0:
            x = x*(-1)
        if y<0:
            y = y*(-1)

        return [x,y]

    def get_image_resolution(self, news):
        if not news.image:
            return None
            
        dementions = NewsDetailSerializer.get_dementions(news)
        return {
            'width': dementions[0],
            'height': dementions[1]
        }


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
