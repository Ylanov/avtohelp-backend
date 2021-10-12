from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext_lazy as _
from fcm_django import models as fcm_models

from roadhelpbackend import celery as tasks
from utils.mixins import BaseMixin, ImageMixin

from .managers import (
    BlackListManager,
    FCMDeviceManager,
    FriendRequestManager,
    ProfileGalleryManager,
)
from .query_set import (
    BlackListQuerySet,
    FriendListQuerySet,
    FriendRequestQuerySet,
    ProfileGalleryQuerySet,
    ProfileQuerySet,
)


class FCMDevice(fcm_models.AbstractFCMDevice):
    """Firebase Cloud Messaging model"""

    user = models.ForeignKey(
        "account.User",
        blank=True,
        null=True,
        related_name="fcm_user",
        on_delete=models.CASCADE,
    )

    objects = FCMDeviceManager()

    class Meta:
        verbose_name = _("FCM device")
        verbose_name_plural = _("FCM devices")


class Profile(BaseMixin, ImageMixin):
    """Profile model"""

    user = models.OneToOneField("account.User", on_delete=models.PROTECT)
    first_name = models.CharField(
        max_length=255, null=True, blank=True, default=None, verbose_name=_("Name")
    )
    last_name = models.CharField(
        max_length=255, null=True, blank=True, default=None, verbose_name=_("Last name")
    )
    city = models.ForeignKey(
        "catalog.City", on_delete=models.CASCADE, blank=True, null=True, default=None
    )
    is_verified = models.BooleanField(
        default=False, null=True, blank=True, verbose_name=_("Verified user")
    )

    objects = ProfileQuerySet.as_manager()

    class Meta:
        """Meta class."""

        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def get_car_info(self):
        """Get str representation of user car"""
        profile_car = self.user.profilecar_set.first()
        return (
            f"{profile_car.car.mark} {profile_car.car.car_model} {profile_car.color}"
            if profile_car
            else None
        )


class ProfileCar(BaseMixin):
    """User profile car"""

    owner = models.ForeignKey("account.User", on_delete=models.PROTECT)
    car = models.ForeignKey("car.Car", on_delete=models.PROTECT)
    color = models.ForeignKey("car.CarColor", on_delete=models.CASCADE)
    license_plate = models.CharField(
        max_length=255,
        verbose_name=_("License plate"),
        blank=True,
        null=False,
        default="",
    )

    class Meta:
        """Meta class"""

        verbose_name = _("Profile car")
        verbose_name_plural = _("Profile cars")


class ProfileLocation(BaseMixin):
    """Profile location"""

    user = models.OneToOneField("account.User", on_delete=models.PROTECT)
    location = gis_models.PointField(_("Location"), blank=True, null=True, default=None)

    class Meta:
        """Meta class."""

        verbose_name = _("Profile location")
        verbose_name_plural = _("Profile locations")


class ProfileGallery(BaseMixin, ImageMixin):
    """Profile gallery"""

    profile = models.ForeignKey(
        "Profile",
        blank=True,
        null=True,
        default=None,
        on_delete=models.CASCADE,
        related_name="gallery",
    )

    objects = ProfileGalleryManager.from_queryset(ProfileGalleryQuerySet)()

    class Meta:
        """Meta class."""

        verbose_name = _("Gallery item")
        verbose_name_plural = _("Gallery items")


class FriendRequest(BaseMixin):
    """Friend request model"""

    owner = models.ForeignKey(
        "account.User", verbose_name=_("Owner"), on_delete=models.CASCADE
    )
    invited = models.ForeignKey(
        "account.User",
        verbose_name=_("Invited user"),
        related_name="friendrequest_invited",
        on_delete=models.CASCADE,
    )
    approved = models.BooleanField(default=False, verbose_name=_("Status"))

    objects = FriendRequestManager.from_queryset(FriendRequestQuerySet)()

    class Meta:
        """Meta-class"""

        verbose_name = _("Friend request")
        verbose_name_plural = _("Friend request")
        unique_together = (
            "owner",
            "invited",
        )

    def approve(self, owner, invited):
        """Approve friend request"""
        # update flag
        self.approved = True
        self.save()
        # create new record in FriendList
        FriendList.objects.create(owner=owner, friend=invited, request=self)
        return self

    def send_push_notification(self):
        """Sent PUSH-notification to invited user"""
        if settings.USE_CELERY:
            tasks.notify_friend_request.delay(self.invited.id)
        else:
            tasks.notify_friend_request(self.invited.id)


class FriendList(BaseMixin):
    """Friend-list model"""

    owner = models.ForeignKey(
        "account.User",
        verbose_name=_("Owner"),
        related_name="friendlist_owner",
        on_delete=models.CASCADE,
    )
    friend = models.ForeignKey(
        "account.User",
        verbose_name=_("Friend"),
        related_name="friendlist_user",
        on_delete=models.CASCADE,
    )
    request = models.ForeignKey(
        "FriendRequest",
        verbose_name=_("Request"),
        related_name="friendlist_request",
        on_delete=models.CASCADE,
    )

    objects = FriendListQuerySet.as_manager()

    class Meta:
        """Meta-class"""

        verbose_name = _("Friend list")
        verbose_name_plural = _("Friend lists")
        unique_together = (
            "owner",
            "friend",
        )


class BlackList(BaseMixin):
    """BlackList model"""

    owner = models.ForeignKey(
        "account.User",
        verbose_name=_("Owner"),
        related_name="blacklist_owner",
        on_delete=models.CASCADE,
    )
    foe = models.ForeignKey(
        "account.User",
        verbose_name=_("Foe"),
        related_name="blacked_user",
        on_delete=models.CASCADE,
    )

    objects = BlackListManager.from_queryset(BlackListQuerySet)()

    class Meta:
        """Meta-class"""

        verbose_name = _("Black list")
        verbose_name_plural = _("Black lists")
        unique_together = (
            "owner",
            "foe",
        )
