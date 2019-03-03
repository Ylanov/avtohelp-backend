from rest_framework import serializers, exceptions
from fcm_django.models import FCMDevice
from userprofile import models
from django.contrib.gis.geos import Point


class FCMDeviceSerializer(serializers.ModelSerializer):
    """FCM Device model serializer"""
    class Meta:
        model = FCMDevice
        fields = ('id', 'name', 'registration_id', 'device_id',
                  'active', 'date_created', 'type')
        read_only_fields = ('id', 'date_created',)
        extra_kwargs = {'active': {'default': True}}

    def validate(self, attrs):
        regid = attrs.get('registration_id')
        dtype = attrs.get('type')
        if regid and dtype and self.Meta.model.objects.filter(
                registration_id=regid).exclude(type=dtype).count():
            raise exceptions.ValidationError(
                {'registration_id': 'This field must be unique.'})
        return attrs

    def __init__(self, *args, **kwargs):
        super(FCMDeviceSerializer, self).__init__(*args, **kwargs)
        self.fields['type'].help_text = (
            'Should be one of ["%s"]' %
            '", "'.join([i for i in self.fields['type'].choices]))

    def create(self, validated_data):
        user = self.context['request'].user
        if not user.is_anonymous:
            validated_data['user'] = user
        device = FCMDevice.objects.create(**validated_data)
        return device

    def update(self, instance, validated_data):

        user = self.context['request'].user
        if not user.is_anonymous:
            instance.user = user
            instance.save()
        else:
            instance.user = None
            instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for retrieving user profile"""

    # RESPONSE
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    avatar = serializers.ImageField(read_only=True)
    city_id = serializers.IntegerField(read_only=True)
    geo_lat = serializers.SerializerMethodField(read_only=True)
    geo_lon = serializers.SerializerMethodField(read_only=True)
    friends_id = serializers.IntegerField(read_only=True)
    blacklist_id = serializers.IntegerField(read_only=True)
    # REQUEST
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    middle_name = serializers.CharField()

    class Meta:
        """Meta class"""

        model = models.Profile
        fields = ('id', 'user_id', 'first_name', 'last_name', 'middle_name',
                  'avatar', 'city_id', 'geo_lat', 'geo_lon', 'friends_id', 'blacklist_id')

    def get_geo_lat(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.location, Point):
            return obj.location.y

    def get_geo_lon(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.location, Point):
            return obj.location.x

    def update(self, instance, validated_data):
        """Override update method"""
        return super().update(instance, validated_data)


class CarListSerializer(serializers.ModelSerializer):
    """Car list serialzier"""

    class Meta:
        """Meta model"""

        model = models.Car
        fields = ('id', 'created', 'user')


class CarDetailSerializer(serializers.ModelSerializer):
    """Car detail serialzier"""

    class Meta:
        """Meta model"""

        model = models.Car
        fields = ('id', 'created', 'modified', 'user', 'mark',
                  'model', 'color', 'license_plate')
