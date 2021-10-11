from django.contrib.gis.geos import Point
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers, exceptions

from car import models as car_models
from car.serializers import current as car_serializers
from catalog import models as catalog_models
from catalog.serializers import current as catalog_serializers
from userprofile import models
from userprofile.models import FCMDevice
from utils import api_exceptions
from utils.serializers import GeoLocationSerializerMixin


class FCMDeviceSerializer(serializers.ModelSerializer):
    """FCM Device model serializer"""

    class Meta:
        model = FCMDevice
        fields = (
            "id",
            "name",
            "registration_id",
            "device_id",
            "active",
            "date_created",
            "type",
        )
        read_only_fields = (
            "id",
            "date_created",
        )
        extra_kwargs = {"active": {"default": True}}

    def validate(self, attrs):
        regid = attrs.get("registration_id")
        dtype = attrs.get("type")
        if (
            regid
            and dtype
            and self.Meta.model.objects.filter(registration_id=regid)
            .exclude(type=dtype)
            .count()
        ):
            raise exceptions.ValidationError(
                {"registration_id": "This field must be unique."}
            )
        return attrs

    def __init__(self, *args, **kwargs):
        super(FCMDeviceSerializer, self).__init__(*args, **kwargs)
        self.fields["type"].help_text = 'Should be one of ["%s"]' % '", "'.join(
            [i for i in self.fields["type"].choices]
        )

    def create(self, validated_data):
        user = self.context["request"].user
        if not user.is_anonymous:
            validated_data["user"] = user
        device = FCMDevice.objects.create(**validated_data)
        return device

    def update(self, instance, validated_data):

        user = self.context["request"].user
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

    color_name = serializers.CharField(source="color.name")
    car_detail = car_serializers.CarDetailSerializer(source="car")

    class Meta:
        """meta model"""

        model = models.ProfileCar
        fields = (
            "id",
            "created",
            "modified",
            "color_name",
            "license_plate",
            "car_detail",
        )


class ProfileViewSerializer(serializers.ModelSerializer):
    """Profile serializer for Requests"""

    profile_car = ProfileCarDetailSerializer(source="user.profilecar_set.first")

    class Meta:
        """Meta class"""

        model = models.Profile
        fields = ("id", "first_name", "last_name", "profile_car")


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for retrieving user profile"""

    # RESPONSE
    phone = PhoneNumberField(read_only=True, source="user.phone")
    city_detail = catalog_serializers.CityDetailSerializer(
        source="city", read_only=True
    )
    profile_car = ProfileCarDetailSerializer(
        source="user.profilecar_set.first", read_only=True
    )
    # ANNOTATED FIELDS
    friend = serializers.BooleanField()
    foe = serializers.BooleanField()
    friend_request = serializers.BooleanField()
    online = serializers.BooleanField()
    is_verified = serializers.BooleanField()

    # REQUEST
    avatar = serializers.ImageField(source="image")
    city = serializers.PrimaryKeyRelatedField(
        queryset=catalog_models.City.objects.all(), write_only=True
    )

    class Meta:
        """Meta class"""

        model = models.Profile
        fields = (
            "id",
            "created",
            "first_name",
            "last_name",
            "avatar",
            "phone",
            "city",
            "city_detail",
            "profile_car",
            "friend",
            "foe",
            "online",
            "friend_request",
            "is_verified",
        )


class MyProfileSerializer(serializers.ModelSerializer):
    """Serializer for retrieving user profile"""

    # RESPONSE
    phone = PhoneNumberField(source="user.phone", read_only=True)
    city_detail = catalog_serializers.CityDetailSerializer(
        source="city", read_only=True
    )
    profile_car = ProfileCarDetailSerializer(
        source="user.profilecar_set.first", read_only=True
    )

    # REQUEST
    city = serializers.PrimaryKeyRelatedField(
        queryset=catalog_models.City.objects.all(), write_only=True
    )
    avatar = serializers.ImageField(source="image")

    class Meta:
        """Meta class"""

        model = models.Profile
        fields = (
            "id",
            "created",
            "first_name",
            "last_name",
            "avatar",
            "phone",
            "city",
            "city_detail",
            "profile_car",
            "is_verified",
        )


class ProfileChangeAvatar(serializers.ModelSerializer):
    """Serializer for update/upload user profile avatar"""

    # COMMON
    avatar = serializers.ImageField(source="image")

    class Meta:
        """Meta class"""

        model = models.Profile
        fields = ("avatar",)


class ProfileCarCreateSerializer(serializers.ModelSerializer):
    """Serializer class for ProfileCarCreateView"""

    color = serializers.PrimaryKeyRelatedField(
        queryset=car_models.CarColor.objects.all(), write_only=True
    )
    car = serializers.PrimaryKeyRelatedField(queryset=car_models.Car.objects.all())

    # RESPONSE
    color_name = serializers.CharField(source="color.name", read_only=True)
    car_detail = car_serializers.CarDetailSerializer(source="car", read_only=True)

    class Meta:
        """meta model"""

        model = models.ProfileCar
        fields = (
            "id",
            "created",
            "modified",
            "color",
            "car",
            "color_name",
            "license_plate",
            "car_detail",
        )

    def create(self, validated_data):
        """Override validated data"""
        validated_data["owner"] = self.context.get("request").user
        return super(ProfileCarCreateSerializer, self).create(validated_data)


class ProfileLocationUpdateSerializer(
    GeoLocationSerializerMixin, serializers.ModelSerializer
):
    """Serializer for ProfileLocation"""

    # REQUEST
    geo_lat = serializers.FloatField(allow_null=True)
    geo_lon = serializers.FloatField(allow_null=True)

    class Meta:
        """Meta class"""

        model = models.ProfileLocation
        fields = ("geo_lat", "geo_lon")

    def validate(self, attrs):
        # if geo_lat and geo_lon was sent
        geo_lat = attrs.pop("geo_lat") if "geo_lat" in attrs else None
        geo_lon = attrs.pop("geo_lon") if "geo_lon" in attrs else None
        if geo_lat and geo_lon:
            # Point(longitude, latitude)
            attrs["location"] = Point(geo_lat, geo_lon)
        return attrs

    def to_representation(self, instance):
        """Override to_representation method"""
        if instance.location and isinstance(instance.location, Point):
            # Point(longitude, latitude)
            setattr(instance, "geo_lat", instance.location.x)
            setattr(instance, "geo_lon", instance.location.y)
        else:
            setattr(instance, "geo_lat", float(0))
            setattr(instance, "geo_lon", float(0))
        return super().to_representation(instance)


class ProfileCarListSerializer(serializers.ModelSerializer):
    """Serializer class for ProfileCarCreateView"""

    # RESPONSE
    color_name = serializers.CharField(source="color.name", read_only=True)
    car_detail = car_serializers.CarDetailSerializer(source="car", read_only=True)

    class Meta:
        """meta model"""

        model = models.ProfileCar
        fields = (
            "id",
            "created",
            "modified",
            "color_name",
            "license_plate",
            "car_detail",
        )


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
        fields = (
            "id",
            "created",
            "profile",
            "tiny",
            "small",
            "average",
            "medium",
            "big",
            "large",
        )

    def get_tiny(self, obj):
        """Get image with size tiny"""
        return obj.get_full_image_url(self.context.get("request"), thumbnail_key="tiny")

    def get_small(self, obj):
        """Get image with size small"""
        return obj.get_full_image_url(
            self.context.get("request"), thumbnail_key="small"
        )

    def get_average(self, obj):
        """Get image with size average"""
        return obj.get_full_image_url(
            self.context.get("request"), thumbnail_key="average"
        )

    def get_medium(self, obj):
        """Get image with size medium"""
        return obj.get_full_image_url(
            self.context.get("request"), thumbnail_key="medium"
        )

    def get_big(self, obj):
        """Get image with size big"""
        return obj.get_full_image_url(self.context.get("request"), thumbnail_key="big")

    def get_large(self, obj):
        """Get image with size large"""
        return obj.get_full_image_url(
            self.context.get("request"), thumbnail_key="large"
        )


class ProfileGalleryCreateSerializer(serializers.ModelSerializer):
    """Serializer for ProfileGalleryCreateView"""

    image = serializers.ImageField(required=True)

    class Meta:
        model = models.ProfileGallery
        fields = ("id", "created", "profile_id", "image")

    def create(self, validated_data):
        """Override create method"""
        validated_data["profile"] = self.context.get("request").user.profile
        return super(ProfileGalleryCreateSerializer, self).create(validated_data)


class ProfileGalleryListSerializer(serializers.ModelSerializer):
    """Serializer for ProfileGalleryListView"""

    class Meta:
        model = models.ProfileGallery
        fields = ("id", "created", "profile_id", "image")


class FullProfileSerializer(serializers.ModelSerializer):
    """Serializer for ProfileListView"""

    online = serializers.BooleanField()
    license_plate = serializers.CharField(source="user.get_car_license_plate")
    avatar = serializers.ImageField(source="image")

    class Meta:
        """Meta class"""

        model = models.Profile
        fields = (
            "id",
            "created",
            "first_name",
            "last_name",
            "online",
            "license_plate",
            "avatar",
            "is_verified",
        )


class ProfileListSerializer(FullProfileSerializer):
    """Serializer for ProfileListView"""

    friend = serializers.BooleanField()
    avatar = serializers.ImageField(source="image")

    class Meta:
        """Meta class"""

        model = models.Profile
        fields = (
            "id",
            "created",
            "first_name",
            "last_name",
            "online",
            "friend",
            "license_plate",
            "avatar",
            "is_verified",
        )


class ProfileBaseSerializer(serializers.ModelSerializer):
    """Serializer for model FriendRequest"""

    license_plate = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        """Meta class"""

        model = models.Profile
        fields = (
            "id",
            "created",
            "first_name",
            "last_name",
            "license_plate",
            "avatar",
            "is_verified",
        )

    def get_license_plate(self, obj):
        """Get car id"""
        cars = obj.user.profilecar_set
        if cars.first():
            return cars.first().license_plate
        else:
            return None

    def get_avatar(self, obj):
        """Get avatar full url"""
        return obj.get_full_image_url(request=self.context.get("request"))


# Friend list


class FriendRequestSerializer(serializers.ModelSerializer):
    """Serializer for model FriendRequest"""

    # RESPONSE
    person = serializers.SerializerMethodField()

    class Meta:
        """Meta class"""

        model = models.FriendRequest
        fields = ("id", "created", "person", "approved")

    def get_person(self, obj):
        if obj.owner == self.context.get("request").user:
            return ProfileBaseSerializer(
                obj.invited.profile, context={"request": self.context.get("request")}
            ).data
        else:
            return ProfileBaseSerializer(
                obj.owner.profile, context={"request": self.context.get("request")}
            ).data


class FriendRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for model FriendRequest"""

    # REQUEST
    # Profile of invited user
    profile = serializers.PrimaryKeyRelatedField(
        queryset=models.Profile.objects.filter(user__is_active=True), write_only=True
    )

    # RESPONSE
    # detail of invited user
    person = ProfileBaseSerializer(source="invited.profile", read_only=True)

    class Meta:
        """Meta class"""

        model = models.FriendRequest
        fields = ("id", "created", "person", "profile", "approved")

    def validate(self, attrs):
        """Override validate method"""
        attrs["owner"] = self.context.get("request").user
        attrs["invited"] = attrs.pop("profile").user

        # Check if requested user ID isn't equal
        if attrs["owner"].id == attrs["invited"].id:
            raise api_exceptions.EqualIDError()

        # Check if friend list isn't existed
        if models.FriendList.objects.by_users(attrs["owner"], attrs["invited"]):
            raise api_exceptions.AlreadyFriends(attrs["owner"], attrs["invited"])

        # Check if friend request isn't exists
        if models.FriendRequest.objects.from_me_to_user(
            attrs["owner"], attrs["invited"]
        ).exists():
            raise api_exceptions.FriendRequestAlreadyExists(
                attrs["owner"], attrs["invited"]
            )

        # Check if invited user isn't blacklisted
        if models.BlackList.objects.are_foes(
            owner=attrs["owner"], user=attrs["invited"]
        ):
            raise api_exceptions.AreFoesError(attrs["owner"], attrs["invited"])

        return attrs

    def create(self, validated_data):
        """Override create-method"""
        owner = validated_data["owner"]
        invited = validated_data["invited"]
        # If request is already exists by one of the selected users,
        # set request approved and create a record in DB.
        requests = models.FriendRequest.objects.common(owner, invited)
        if requests.exists():
            request = requests.first()
            # Update flag
            request.approved = True
            request.save()
            # Create new record in FriendList
            models.FriendList.objects.create(
                owner=owner, friend=invited, request=request
            )
            return request
        return models.FriendRequest.objects.make(owner=owner, user=invited)


class FriendRequestApproveSerializer(serializers.ModelSerializer):
    """Serializer for model FriendRequest"""

    class Meta:
        """Meta class"""

        model = models.FriendRequest
        fields = ("approved",)

    def update(self, instance, validated_data):
        """Override update method"""
        return instance.approve(owner=instance.owner, invited=instance.invited)


class ProfileFriendListSerializer(serializers.ModelSerializer):
    """Serializer for model FriendList"""

    person = serializers.SerializerMethodField()

    class Meta:
        """Meta class"""

        model = models.FriendList
        fields = ("id", "created", "person", "request_id")

    def get_person(self, obj):
        """Serializer method for get friend profile"""
        if obj.owner == self.context.get("request").user:
            return ProfileBaseSerializer(
                obj.friend.profile, context={"request": self.context.get("request")}
            ).data
        else:
            return ProfileBaseSerializer(
                obj.owner.profile, context={"request": self.context.get("request")}
            ).data


# Black list


class BlackListCreateSerializer(serializers.ModelSerializer):
    """Serializer class for BlackListRequest"""

    # REQUEST
    profile = serializers.PrimaryKeyRelatedField(
        queryset=models.Profile.objects.all(), write_only=True
    )

    # RESPONSE
    profile_id = serializers.IntegerField(source="foe.profile.id", read_only=True)

    class Meta:
        """Meta class"""

        model = models.BlackList
        fields = ("id", "created", "profile", "profile_id")

    def validate(self, attrs):
        """Override validate method"""
        attrs["owner"] = self.context.get("request").user
        attrs["foe"] = attrs.pop("profile").user

        if attrs["owner"] == attrs["foe"]:
            raise api_exceptions.EqualIDError()
        # Check existed request
        in_pending = models.BlackList.objects.are_foes(
            owner=attrs["owner"], user=attrs["foe"]
        )
        if in_pending:
            raise api_exceptions.AlreadyBlacked(owner=attrs["owner"], user=attrs["foe"])
        return attrs

    def create(self, validated_data):
        """Override create method"""
        # If participants are friends then break the friendship
        qs = models.FriendList.objects.by_users(
            validated_data["owner"], validated_data["foe"]
        )
        if qs.exists():
            friendship = qs.first()
            friendship.request.delete()
            friendship.delete()
        return super(BlackListCreateSerializer, self).create(validated_data)


class BlackListDetailSerializer(serializers.ModelSerializer):
    """Serializer for model BlackList"""

    person = serializers.SerializerMethodField()

    class Meta:
        """Meta class"""

        model = models.BlackList
        fields = ("id", "created", "person")

    def get_person(self, obj):
        if obj.owner == self.context.get("request").user:
            return ProfileBaseSerializer(
                obj.foe.profile, context={"request": self.context.get("request")}
            ).data
        else:
            return ProfileBaseSerializer(
                obj.owner.profile, context={"request": self.context.get("request")}
            ).data
