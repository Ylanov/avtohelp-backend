from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Subquery
from fcm_django.models import FCMDevice
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers, exceptions

from account import models as account_models
from catalog import models as catalog_models
from car import models as car_models
from catalog.serializers import current as catalog_serializers
from car.serializers import current as car_serializers
from userprofile import models
from utils import api_exceptions


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


# NOTE: user utils.serializers.CoordinatesSerializer
class GeoPositonMixin(serializers.ModelSerializer):
    """Added additional fields for show geo position in X, Y coord."""

    geo_lat = serializers.SerializerMethodField(read_only=True, allow_null=True)
    geo_lon = serializers.SerializerMethodField(read_only=True, allow_null=True)

    class Meta:
        """Meta class"""
        model = models.Profile
        fields = ('geo_lat', 'geo_lon')

    def get_geo_lat(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.user.profilelocation.location, Point):
            return obj.user.profilelocation.location.y

    def get_geo_lon(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.user.profilelocation.location, Point):
            return obj.user.profilelocation.location.x


class ProfileCarDetailSerializer(serializers.ModelSerializer):
    """Serializer for ProfileCar"""

    color_name = serializers.CharField(source='color.name')
    car = car_serializers.CarDetailSerializer()

    class Meta:
        """meta model"""

        model = models.ProfileCar
        fields = ('id', 'created', 'modified', 'color_name', 'license_plate', 'car')


class ProfileViewSerializer(serializers.ModelSerializer):
    """Profile serializer for Requests"""

    phone = serializers.CharField(source='user.phone')
    profile_car = ProfileCarDetailSerializer(source='user.profilecar_set.first')

    class Meta:
        """Meta class"""

        model = models.Profile
        fields = ('id', 'first_name', 'last_name', 'middle_name',
                  'phone', 'profile_car'
                  )


# NOTE: user utils.serializers.CoordinatesSerializer
class ProfileSerializer(GeoPositonMixin):
    """Serializer for retrieving user profile"""

    # RESPONSE
    phone = PhoneNumberField(read_only=True, source='user.phone')
    city_detail = catalog_serializers.CityDetailSerializer(source='city', read_only=True)
    car = ProfileCarDetailSerializer(source='user.profilecar_set.first', read_only=True)
    #   or  #
    # car = serializers.CharField(source='get_car_info')

    # REQUEST
    city = serializers.PrimaryKeyRelatedField(queryset=catalog_models.City.objects.all(),
                                              write_only=True)

    class Meta:
        """Meta class"""

        model = models.Profile
        fields = ('id', 'created', 'first_name', 'last_name', 'middle_name',
                  'phone', 'avatar', 'city', 'city_detail',
                  'car', 'geo_lat', 'geo_lon')

    def get_geo_lat(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.user.profilelocation.location, Point):
            return obj.user.profilelocation.location.y

    def get_geo_lon(self, obj):
        """Point(longitude, latitude)"""
        if isinstance(obj.user.profilelocation.location, Point):
            return obj.user.profilelocation.location.x


class ProfileCarCreateSerializer(serializers.ModelSerializer):
    """Serializer class for ProfileCarCreateView"""

    color = serializers.PrimaryKeyRelatedField(queryset=car_models.CarColor.objects.all(),
                                               write_only=True)
    mark = serializers.PrimaryKeyRelatedField(source='car.mark', queryset=car_models.CarMark.objects.all(),
                                              write_only=True)
    car_model = serializers.PrimaryKeyRelatedField(source='car.car_model', queryset=car_models.CarModel.objects.all(),
                                                   write_only=True)
    license_plate = serializers.CharField()

    # RESPONSE
    color_name = serializers.CharField(source='color.name', read_only=True)
    car = car_serializers.CarDetailSerializer(read_only=True)

    class Meta:
        """meta model"""

        model = models.ProfileCar
        fields = ('id', 'created', 'modified', 'color',
                  'mark', 'car_model', 'color_name', 'license_plate',
                  'car'
                  )

    def create(self, validated_data):
        """Override validated data"""
        validated_data['owner'] = self.context.get('request').user
        validated_data['car'] = car_models.Car.objects.get(**validated_data.pop('car'))
        return super(ProfileCarCreateSerializer, self).create(validated_data)


class ProfileCarListSerializer(serializers.ModelSerializer):
    """Serializer class for ProfileCarCreateView"""

    # RESPONSE
    color_name = serializers.CharField(source='color.name', read_only=True)
    car = car_serializers.CarDetailSerializer(read_only=True)

    class Meta:
        """meta model"""

        model = models.ProfileCar
        fields = ('id', 'created', 'modified', 'color_name',
                  'license_plate', 'car')


class ProfileListSerializer(GeoPositonMixin):
    """Serializer for ProfileListView"""

    class Meta:
        """Meta class"""
        model = models.Profile
        fields = ('id', 'created', 'user_id', 'avatar',
                  'first_name', 'last_name', 'geo_lat',
                  'geo_lon')


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
        fields = ('id', 'created', 'foe')


class FriendRequestPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """Override PrimaryKeyRelatedField"""

    def to_internal_value(self, data):
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)
        try:
            request_user = self.context.get('request').user
            if request_user.id == data:
                raise api_exceptions.EqualIDError()
            qs = self.get_queryset().filter(
                # Get all users in qs that are NOT in my FriendRequest
                ~Q(id__in=Subquery(models.FriendRequest.objects.my_requests(request_user).values('invited__id'))))
            return qs.get(pk=data)
        except ObjectDoesNotExist:
            raise api_exceptions.FriendRequestAlreadyExists(owner=request_user.id,
                                                            invited=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)


class FriendRequestDetailSerializer(GeoPositonMixin):
    """Serializer for model FriendRequest"""

    car = serializers.CharField(source='get_car_info')

    class Meta:
        """Meta class"""
        model = models.Profile
        fields = ('id', 'created', 'user_id', 'first_name',
                  'last_name', 'car', 'geo_lat', 'geo_lon')


class FriendRequestSerializer(serializers.ModelSerializer):
    """Serializer for model FriendRequest"""

    # REQUEST
    # invited user
    user = FriendRequestPrimaryKeyRelatedField(queryset=account_models.User.objects.all(),
                                               source='invited',
                                               write_only=True)

    # RESPONSE
    # detail of invited user
    invited = FriendRequestDetailSerializer(source='invited.profile', read_only=True)

    class Meta:
        """Meta class"""
        model = models.FriendRequest
        fields = ('id', 'created', 'invited', 'user', 'approved')

    def create(self, validated_data):
        """Override create-method"""
        validated_data['owner'] = self.context.get('request').user
        friend_request = models.FriendRequest.objects.make(owner=validated_data['owner'],
                                                           user=validated_data['invited'])
        return friend_request


class FriendRequestApproveSerializer(serializers.ModelSerializer):
    """Serializer for model FriendRequest"""

    class Meta:
        """Meta class"""
        model = models.FriendRequest
        fields = ('approved',)

    def update(self, instance, validated_data):
        """Override update method"""
        instance.approved = True
        instance.save()
        return instance


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


class BlackListCreateSerializer(serializers.ModelSerializer):
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
