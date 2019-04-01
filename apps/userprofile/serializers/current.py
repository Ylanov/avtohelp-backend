from os.path import exists

from fcm_django.models import FCMDevice
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers, exceptions

from car import models as car_models
from car.serializers import current as car_serializers
from catalog import models as catalog_models
from catalog.serializers import current as catalog_serializers
from userprofile import models
from utils import api_exceptions
from utils.serializers import GeoPositonMixin


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


# Profile


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
                  'phone', 'profile_car')


class ProfileSerializer(serializers.ModelSerializer, GeoPositonMixin):
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
                  'phone', 'city', 'city_detail',
                  'car', 'geo_lat', 'geo_lon')


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
                  'car')

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


class ProfileAvatarSerializer(serializers.ModelSerializer):
    """Serializer method for ProfileGallery model"""

    tiny = serializers.SerializerMethodField()
    small = serializers.SerializerMethodField()
    average = serializers.SerializerMethodField()
    medium = serializers.SerializerMethodField()
    big = serializers.SerializerMethodField()
    large = serializers.SerializerMethodField()

    class Meta:
        """Meta class"""
        model = models.ProfileGallery
        fields = ('id', 'created', 'tiny', 'small',
                  'average', 'medium', 'big', 'large', 'is_main')

    def get_tiny(self, obj):
        """Get image with size tiny"""
        return obj.image['tiny'].url if obj.image and exists(obj.image.path) else None

    def get_small(self, obj):
        """Get image with size small"""
        return obj.image['small'].url if obj.image and exists(obj.image.path) else None

    def get_average(self, obj):
        """Get image with size average"""
        return obj.image['average'].url if obj.image and exists(obj.image.path) else None

    def get_medium(self, obj):
        """Get image with size medium"""
        return obj.image['medium'].url if obj.image and exists(obj.image.path) else None

    def get_big(self, obj):
        """Get image with size big"""
        return obj.image['big'].url if obj.image and exists(obj.image.path) else None

    def get_large(self, obj):
        """Get image with size large"""
        return obj.image['large'].url if obj.image and exists(obj.image.path) else None


class ProfileGalleryCreateSerializer(serializers.ModelSerializer):
    """Serializer for ProfileGalleryCreateView"""

    image = serializers.ImageField(required=True)

    class Meta:
        model = models.ProfileGallery
        fields = ('id', 'created', 'profile', 'image', 'is_main')

    def create(self, validated_data):
        """Override create method"""
        validated_data['profile'] = self.context.get('request').user.profile
        return super(ProfileGalleryCreateSerializer, self).create(validated_data)


class ProfileGallerySetMainSerializer(serializers.ModelSerializer):
    """Serializer for ProfileGalleryCreateView"""
    class Meta:
        model = models.ProfileGallery
        fields = ('is_main',)

    def update(self, instance, validated_data):
        """Override update method"""
        validated_data['is_main'] = True
        models.ProfileGallery.objects.reset_status(profile=self.context.get('request').user.profile)
        return super(ProfileGallerySetMainSerializer, self).update(instance, validated_data)


class ProfileGalleryListSerializer(serializers.ModelSerializer):
    """Serializer for ProfileGalleryListView"""
    class Meta:
        model = models.ProfileGallery
        fields = ('id', 'created', 'profile', 'image', 'is_main')


class ProfileListSerializer(serializers.ModelSerializer, GeoPositonMixin):
    """Serializer for ProfileListView"""
    online = serializers.BooleanField()
    friend = serializers.BooleanField()
    license_plate = serializers.CharField(source='user.get_car_license_plate')

    class Meta:
        """Meta class"""
        model = models.Profile
        fields = ('id', 'created', 'first_name', 'last_name',
                  'middle_name', 'geo_lat', 'geo_lon', 'online',
                  'friend', 'license_plate')


# Friend list


class FriendRequestDetailSerializer(serializers.ModelSerializer, GeoPositonMixin):
    """Serializer for model FriendRequest"""

    car = ProfileCarDetailSerializer(source='user.profilecar_set.first')

    class Meta:
        """Meta class"""
        model = models.Profile
        fields = ('id', 'created', 'first_name', 'last_name',
                  'car', 'geo_lat', 'geo_lon')


class FriendRequestSerializer(serializers.ModelSerializer):
    """Serializer for model FriendRequest"""

    # RESPONSE
    person = serializers.SerializerMethodField()

    class Meta:
        """Meta class"""
        model = models.FriendRequest
        fields = ('id', 'created', 'person', 'approved')

    def get_person(self, obj):
        if obj.owner == self.context.get('request').user:
            return FriendRequestDetailSerializer(obj.invited.profile).data
        else:
            return FriendRequestDetailSerializer(obj.owner.profile).data


class FriendRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for model FriendRequest"""

    # REQUEST
    # Profile of invited user
    profile = serializers.PrimaryKeyRelatedField(queryset=models.Profile.objects.all(),
                                                 write_only=True)

    # RESPONSE
    # detail of invited user
    person = FriendRequestDetailSerializer(source='invited.profile', read_only=True)

    class Meta:
        """Meta class"""
        model = models.FriendRequest
        fields = ('id', 'created', 'person', 'profile', 'approved')

    def validate(self, attrs):
        """Override validate method"""
        attrs['owner'] = self.context.get('request').user
        attrs['invited'] = attrs.pop('profile').user

        if attrs['owner'].id == attrs['invited'].id:
            raise api_exceptions.EqualIDError()
        # Check existed request
        in_pending = models.FriendRequest.objects.waiting(user=attrs['owner'],
                                                          invited=attrs['invited'])
        if in_pending:
            raise api_exceptions.FriendRequestAlreadyExists(owner=attrs['owner'].id,
                                                            invited=attrs['invited'].id)
        return attrs

    def create(self, validated_data):
        """Override create-method"""
        return models.FriendRequest.objects.make(owner=validated_data['owner'],
                                                 user=validated_data['invited'])


class FriendRequestApproveSerializer(serializers.ModelSerializer):
    """Serializer for model FriendRequest"""

    class Meta:
        """Meta class"""
        model = models.FriendRequest
        fields = ('approved',)

    def update(self, instance, validated_data):
        """Override update method"""
        return instance.approve(owner=instance.owner, invited=instance.invited)


class ProfileFriendListSerializer(serializers.ModelSerializer):
    """Serializer for model FriendList"""

    friend = serializers.SerializerMethodField()

    class Meta:
        """Meta class"""
        model = models.FriendList
        fields = ('id', 'created', 'friend', 'request_id')

    def get_friend(self, obj):
        if obj.owner == self.context.get('request').user:
            return ProfileViewSerializer(obj.friend.profile).data
        else:
            return ProfileViewSerializer(obj.owner.profile).data


# Black list


class BlackListCreateSerializer(serializers.ModelSerializer):
    """Serializer class for BlackListRequest"""

    # REQUEST
    profile = serializers.PrimaryKeyRelatedField(queryset=models.Profile.objects.all(),
                                                 write_only=True)

    # RESPONSE
    profile_id = serializers.IntegerField(source='foe.profile.id',
                                          read_only=True)

    class Meta:
        """Meta class"""
        model = models.BlackList
        fields = ('id', 'created', 'profile', 'profile_id')

    def validate(self, attrs):
        """Override validate method"""
        attrs['owner'] = self.context.get('request').user
        attrs['foe'] = attrs.pop('profile').user

        if attrs['owner'].id == attrs['foe'].id:
            raise api_exceptions.EqualIDError()
        # Check existed request
        in_pending = models.BlackList.objects.are_foes(owner=attrs['owner'],
                                                       user=attrs['foe'])
        if in_pending:
            raise api_exceptions.AlreadyBlacked(owner=attrs['owner'].id,
                                                user=attrs['foe'].id)
        return attrs


class BlackListDetailSerializer(serializers.ModelSerializer):
    """Serializer for model BlackList"""

    profile_id = FriendRequestDetailSerializer(source='foe.profile', read_only=True)

    class Meta:
        """Meta class"""
        model = models.BlackList
        fields = ('id', 'created', 'profile_id')


class BlackListSerializer(serializers.ModelSerializer):
    """Serializer for model BlackList"""

    foe = serializers.SerializerMethodField()

    class Meta:
        """Meta class"""
        model = models.BlackList
        fields = ('id', 'created', 'foe')

    def get_foe(self, obj):
        if obj.owner == self.context.get('request').user:
            return ProfileViewSerializer(obj.foe.profile).data
        else:
            return ProfileViewSerializer(obj.owner.profile).data
