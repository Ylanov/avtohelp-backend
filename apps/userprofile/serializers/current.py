from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Subquery
from fcm_django.models import FCMDevice
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers, exceptions

from account import models as account_models
from userprofile import models
from catalog import models as catalog_models
from utils import mixins, api_exceptions


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


class CarCreateSerializer(serializers.ModelSerializer):
    """Serializer for update or create car information"""

    mark = serializers.PrimaryKeyRelatedField(queryset=catalog_models.CarMark.objects.all())
    model = serializers.PrimaryKeyRelatedField(queryset=catalog_models.CarModel.objects.all())
    color = serializers.PrimaryKeyRelatedField(queryset=catalog_models.CarColor.objects.all())
    license_plate = serializers.CharField()

    class Meta:
        """Meta class"""

        model = models.Car
        fields = ('mark', 'model', 'color', 'license_plate')

    def create(self, validated_data):
        """Override create method"""
        import ipdb; ipdb.set_trace()
        validated_data['user'] = self.context.get('request').user
        return super(CarCreateSerializer, self).create(validated_data)


class ProfileSerializer(serializers.ModelSerializer, mixins.ProfileMixin):
    """Serializer for retrieving user profile"""

    # RESPONSE
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    # geo_lat = serializers.SerializerMethodField(read_only=True)
    # geo_lon = serializers.SerializerMethodField(read_only=True)
    friends_id = serializers.IntegerField(read_only=True)
    blacklist_id = serializers.IntegerField(read_only=True)
    phone = PhoneNumberField(read_only=True, source='user.phone')
    # REQUEST
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    middle_name = serializers.CharField()
    avatar = serializers.ImageField()
    city_id = serializers.IntegerField()
    # car = CarCreateSerializer(source='user.car', write_only=True)

    class Meta:
        """Meta class"""

        model = models.Profile
        fields = ('id', 'user_id', 'first_name', 'last_name', 'middle_name',
                  'phone', 'avatar', 'city_id', 'friends_id', 'blacklist_id',
                  # 'car'
                  #'geo_lat', 'geo_lon'
                  )

    def get_geo_lat(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.location, Point):
            return obj.location.y

    def get_geo_lon(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.location, Point):
            return obj.location.x


class ProfileListSerializer(serializers.ModelSerializer):
    """Serializer for ProfileListView"""

    license_plate = serializers.CharField(source='user.car_set.first.license_plate', allow_null=True)

    class Meta:
        """Meta class"""
        model = models.Profile
        fields = ('id', 'created', 'user_id', 'avatar',
                  'first_name', 'last_name', 'license_plate')


class ProfileFriendListSerializer(serializers.ModelSerializer):
    """Serializer for model FriendList"""

    class Meta:
        """Meta class"""
        model = models.FriendList
        fields = ('id', 'created', 'friend_id', 'request_id')


class ProfileBlackListSerializer(serializers.ModelSerializer):
    """Serializer for model BlackList"""

    class Meta:
        """Meta class"""
        model = models.BlackList
        fields = ('id', 'created', 'foe_id')


class FriendListPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """Override PrimaryKeyRelatedField"""

    def to_internal_value(self, data):
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)
        try:
            request_user = self.context.get('request').user
            qs = self.get_queryset().filter(
                # Get all users in qs that are NOT in my BlackList
                ~Q(id__in=Subquery(models.FriendRequest.objects.my_list(request_user).values('invited__id'))))
            return qs.get(pk=data)
        except ObjectDoesNotExist:
            raise api_exceptions.AlreadyFriends(owner=request_user.id,
                                                user=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)


class FriendRequestSerializer(serializers.ModelSerializer):
    """Serializer class for FriendRequest"""

    # REQUEST
    user_id = FriendListPrimaryKeyRelatedField(queryset=account_models.User.objects.all(),
                                               source='invited')

    # RESPONSE
    approved = serializers.BooleanField(read_only=True)

    class Meta:
        """Meta class"""
        model = models.FriendRequest
        fields = ('id', 'created', 'user_id', 'approved')

    def create(self, validated_data):
        """Override create-method"""
        validated_data['user'] = self.context.get('request').user
        return super().create(validated_data)


class BlackListPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """Override PrimaryKeyRelatedField"""

    def to_internal_value(self, data):
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)
        try:
            request_user = self.context.get('request').user
            qs = self.get_queryset().filter(
                # Get all users in qs that are NOT in my BlackList
                ~Q(id__in=Subquery(models.BlackList.objects.my_list(request_user).values('foe__id'))))
            return qs.get(pk=data)
        except ObjectDoesNotExist:
            raise api_exceptions.AlreadyBlacked(owner=request_user.id,
                                                user=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)


class BlackListRequestSerializer(serializers.ModelSerializer):
    """Serializer class for BlackListRequest"""

    # REQUEST
    user_id = BlackListPrimaryKeyRelatedField(queryset=account_models.User.objects.filter(),
                                              source='foe')

    class Meta:
        """Meta class"""
        model = models.BlackList
        fields = ('id', 'created', 'user_id')

    def create(self, validated_data):
        """Override create method"""
        validated_data['owner'] = self.context.get('request').user
        return super().create(validated_data)


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
