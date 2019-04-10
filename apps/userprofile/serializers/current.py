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

    profile_car = ProfileCarDetailSerializer(source='user.profilecar_set.first')

    class Meta:
        """Meta class"""

        model = models.Profile
        fields = ('id', 'first_name', 'last_name', 'profile_car')


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for retrieving user profile"""

    # RESPONSE
    phone = PhoneNumberField(read_only=True, source='user.phone')
    city_detail = catalog_serializers.CityDetailSerializer(source='city', read_only=True)
    profile_car = ProfileCarDetailSerializer(source='user.profilecar_set.first', read_only=True)
    # ANNOTATED FIELDS
    friend = serializers.BooleanField()
    foe = serializers.BooleanField()
    online = serializers.BooleanField()

    # REQUEST
    avatar = serializers.ImageField(source='image')
    city = serializers.PrimaryKeyRelatedField(queryset=catalog_models.City.objects.all(),
                                              write_only=True)

    class Meta:
        """Meta class"""

        model = models.Profile
        fields = ('id', 'created', 'first_name', 'last_name', 'avatar',
                  'phone', 'city', 'city_detail', 'profile_car', 'friend',
                  'foe', 'online')


class MyProfileSerializer(serializers.ModelSerializer):
    """Serializer for retrieving user profile"""

    # RESPONSE
    phone = PhoneNumberField(source='user.phone', read_only=True, )
    city_detail = catalog_serializers.CityDetailSerializer(source='city', read_only=True)
    profile_car = ProfileCarDetailSerializer(source='user.profilecar_set.first', read_only=True)

    # REQUEST
    city = serializers.PrimaryKeyRelatedField(queryset=catalog_models.City.objects.all(),
                                              write_only=True)

    # COMMON
    avatar = serializers.ImageField(source='image')

    class Meta:
        """Meta class"""

        model = models.Profile
        fields = ('id', 'created', 'first_name', 'last_name', 'avatar',
                  'phone', 'city', 'city_detail', 'profile_car')


class ProfileCarCreateSerializer(serializers.ModelSerializer):
    """Serializer class for ProfileCarCreateView"""

    color = serializers.PrimaryKeyRelatedField(queryset=car_models.CarColor.objects.all(),
                                               write_only=True)
    car = serializers.PrimaryKeyRelatedField(queryset=car_models.Car.objects.all(),
                                             write_only=True)
    license_plate = serializers.CharField()

    # RESPONSE
    color_name = serializers.CharField(source='color.name', read_only=True)
    profile_car = car_serializers.CarDetailSerializer(source='car', read_only=True)

    class Meta:
        """meta model"""

        model = models.ProfileCar
        fields = ('id', 'created', 'modified', 'color', 'car',
                  'color_name', 'license_plate', 'profile_car')

    def create(self, validated_data):
        """Override validated data"""
        validated_data['owner'] = self.context.get('request').user
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


class ProfileGalleryDetailSerializer(serializers.ModelSerializer):
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
        fields = ('id', 'created', 'profile', 'tiny', 'small',
                  'average', 'medium', 'big', 'large')

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
        fields = ('id', 'created', 'profile_id', 'image')

    def create(self, validated_data):
        """Override create method"""
        validated_data['profile'] = self.context.get('request').user.profile
        return super(ProfileGalleryCreateSerializer, self).create(validated_data)


class ProfileGalleryListSerializer(serializers.ModelSerializer):
    """Serializer for ProfileGalleryListView"""
    class Meta:
        model = models.ProfileGallery
        fields = ('id', 'created', 'profile', 'image')


class FullProfileSerializer(serializers.ModelSerializer):
    """Serializer for ProfileListView"""
    online = serializers.BooleanField()
    license_plate = serializers.CharField(source='user.get_car_license_plate')
    avatar = serializers.ImageField(source='image')

    class Meta:
        """Meta class"""
        model = models.Profile
        fields = ('id', 'created', 'first_name', 'last_name',
                  'online', 'license_plate', 'avatar')


class ProfileListSerializer(FullProfileSerializer):
    """Serializer for ProfileListView"""

    friend = serializers.BooleanField()
    avatar = serializers.ImageField(source='image')

    class Meta:
        """Meta class"""
        model = models.Profile
        fields = ('id', 'created', 'first_name', 'last_name',
                  'online', 'friend', 'license_plate', 'avatar')


class ProfileBaseSerializer(serializers.ModelSerializer):
    """Serializer for model FriendRequest"""

    license_plate = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        """Meta class"""
        model = models.Profile
        fields = ('id', 'created', 'first_name', 'last_name',
                  'license_plate', 'avatar')

    def get_license_plate(self, obj):
        """Get car id"""
        cars = obj.user.profilecar_set
        if cars.first():
            return cars.first().license_plate
        else:
            return None

    def get_avatar(self, obj):
        """Get avatar full url"""
        if obj.image and hasattr(obj.image, 'url'):
            return self.context.get('request').build_absolute_uri(obj.image.url)
        else:
            return None


# Friend list


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
            return ProfileBaseSerializer(obj.invited.profile, context={'request': self.context.get('request')}).data
        else:
            return ProfileBaseSerializer(obj.owner.profile, context={'request': self.context.get('request')}).data


class FriendRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for model FriendRequest"""

    # REQUEST
    # Profile of invited user
    profile = serializers.PrimaryKeyRelatedField(queryset=models.Profile.objects.all(),
                                                 write_only=True)

    # RESPONSE
    # detail of invited user
    person = ProfileBaseSerializer(source='invited.profile', read_only=True)

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
        return attrs

    def create(self, validated_data):
        """Override create-method"""
        owner = validated_data['owner']
        invited = validated_data['invited']
        # If request is already exists by one of the selected users,
        # set request approved and create a record in DB.
        requests = models.FriendRequest.objects.common(owner, invited)
        if requests.exists():
            request = requests.first()
            # Update flag
            request.approved = True
            request.save()
            # Create new record in FriendList
            models.FriendList.objects.create(owner=owner, friend=invited, request=request)
            return request
        return models.FriendRequest.objects.make(owner=owner,
                                                 user=invited)


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

    person = serializers.SerializerMethodField()

    class Meta:
        """Meta class"""
        model = models.FriendList
        fields = ('id', 'created', 'person', 'request_id')

    def get_person(self, obj):
        """Serializer method for get friend profile"""
        if obj.owner == self.context.get('request').user:
            return ProfileBaseSerializer(obj.friend.profile, context={'request': self.context.get('request')}).data
        else:
            return ProfileBaseSerializer(obj.owner.profile, context={'request': self.context.get('request')}).data


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

    person = serializers.SerializerMethodField()

    class Meta:
        """Meta class"""
        model = models.BlackList
        fields = ('id', 'created', 'person')

    def get_person(self, obj):
        if obj.owner == self.context.get('request').user:
            return ProfileBaseSerializer(obj.foe.profile, context={'request': self.context.get('request')}).data
        else:
            return ProfileBaseSerializer(obj.owner.profile, context={'request': self.context.get('request')}).data
