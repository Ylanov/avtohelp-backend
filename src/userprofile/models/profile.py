# type: ignore

from django.conf import settings
from django.contrib.gis.db.models import (
    Manager as GeoManager,
    PointField,
)
from django.contrib.gis.geos import Point
from django.db import models
from django.utils.translation import ugettext_lazy as _

from roadhelpbackend import celery as tasks
from utils.mixins import (
    BaseMixin,
    ImageMixin,
)

from ..managers import (
    FriendRequestManager,
    ProfileGalleryManager,
)
from ..query_set import (
    FriendListQuerySet,
    FriendRequestQuerySet,
    ProfileGalleryQuerySet,
    ProfileQuerySet,
)


class Profile(BaseMixin, ImageMixin):
    """Profile model"""

    user = models.OneToOneField("account.User", on_delete=models.PROTECT)
    first_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default=None,
        verbose_name=_("Name"),
    )
    last_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default=None,
        verbose_name=_("Last name"),
    )
    city = models.ForeignKey(
        "catalog.City",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None,
    )
    is_verified = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        verbose_name=_("Verified user"),
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
            f"{profile_car.car.mark} {profile_car.car.car_model} {profile_car.color}"  # noqa
            if profile_car
            else None
        )


class ProfileLocation(BaseMixin):
    """Profile location"""

    user = models.OneToOneField("account.User", on_delete=models.PROTECT)
    location = PointField(
        _("Location"), blank=True, null=True, default=Point(0, 0)
    )

    lng = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    lat = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)

    gis = GeoManager()
    objects = models.Manager()

    class Meta:
        index_together = ["user", "lng", "lat"]

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
        "account.User",
        verbose_name=_("Owner"),
        on_delete=models.CASCADE,
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
