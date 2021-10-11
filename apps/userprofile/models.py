from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.db.models.functions import Distance
from django.contrib.postgres.search import SearchVector
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from fcm_django import models as fcm_models
from online_users.models import OnlineUserActivity as activity

from base.models import PushNotificationConfiguration
from project import celery as tasks
from utils.mixins import BaseMixin, ImageMixin


class FCMDeviceQuerySet(fcm_models.FCMDeviceQuerySet):
    """Firebase Cloud Messaging querysets"""

    def by_geo_position(self, point):
        """Filter by geo position"""
        configuration = PushNotificationConfiguration.get_solo()
        return self.filter(
            user__profilelocation__location__distance_lte=(
                point,
                Distance(m=configuration.radius),
            )
        )

    def annotate_device_geo_position_relevance(self):
        """Is the device geo-position information current?"""
        geo_pos_settings = PushNotificationConfiguration.get_solo()
        hours, minutes = (
            geo_pos_settings.geo_position_lifetime.hour,
            geo_pos_settings.geo_position_lifetime.minute,
        )

        return self.annotate(
            geo_position_is_valid=models.Case(
                models.When(
                    user__profilelocation__modified__gte=timezone.now()
                    - timezone.timedelta(hours=99, minutes=0),
                    then=True,
                ),
                output_field=models.BooleanField(default=False),
                default=False,
            )
        )

    def annotate_device_distance_from_assistance_request(self, assistance_request):
        """Annotate distance between user device location and assistance request"""
        return self.annotate(
            distance=Distance(
                "user__profilelocation__location", assistance_request.location
            )
        )


class FCMDeviceManager(models.Manager):
    def get_queryset(self):
        return FCMDeviceQuerySet(self.model)


class FCMDevice(fcm_models.AbstractFCMDevice):
    """Firebase Cloud Messaging model"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="fcm_user",
        on_delete=models.CASCADE,
    )

    objects = FCMDeviceManager()

    class Meta:
        verbose_name = _("FCM device")
        verbose_name_plural = _("FCM devices")


class ProfileQuerySet(models.QuerySet):
    """Custom QuerySet for model Profile"""

    def friendly(self, user):
        """
        Queryset that EXCLUDE profiles in which user is owner of blacklist or he is a foe and excluded himself
        :param user:
        :type user: object
        :return: ProfileQuerySet
        """
        return (
            self.exclude(user__blacked_user__owner=user)
            .exclude(user__blacklist_owner__foe=user)
            .exclude(user=user)
        )

    def valid(self):
        """Queryset that exclude profiles with null first name and last name"""
        return self.exclude(first_name__isnull=True, last_name__isnull=True)

    def friends(self, user):
        """
        Queryset that return only friends
        :param user:
        :return: QuerySet
        """
        return self.filter(
            # Check if USER is an initiator of friend request (is OWNER)
            models.Q(user__friendlist_user__owner=user)
            |
            # Check if USER is an invited person
            models.Q(user__friendlist_owner__friend=user)
        ).exclude(user=user)

    def annotate_online_status(self):
        """
        Annotate online status
        :return: annotate field online status
        """
        return self.annotate(
            online=models.Case(
                models.When(
                    models.Q(user__onlineuseractivity__user__isnull=False), then=True
                ),
                default=False,
                output_field=models.BooleanField(default=False),
            )
        )

    def annotate_friend_status(self, user):
        """
        Annotate friend status
        :return: annotated field
        """
        return self.annotate(
            friend=models.Case(
                models.When(
                    Q(
                        user_id__in=models.Subquery(
                            FriendList.objects.common(user).values("friend__id")
                        )
                    )
                    | Q(
                        user_id__in=models.Subquery(
                            FriendList.objects.common(user).values("owner__id")
                        )
                    ),
                    then=True,
                ),
                output_field=models.BooleanField(default=False),
                default=False,
            )
        )

    def annotate_foe_status(self, user):
        """
        Annotate foe status
        :return: annotated field
        """

        return self.annotate(
            foe=models.Case(
                models.When(
                    Q(
                        user_id__in=models.Subquery(
                            BlackList.objects.common(user).values("foe__id")
                        )
                    )
                    | Q(
                        user_id__in=models.Subquery(
                            BlackList.objects.common(user).values("owner__id")
                        )
                    ),
                    then=True,
                ),
                output_field=models.BooleanField(default=False),
                default=False,
            )
        )

    def annotate_friend_request_status(self, user):
        """
        Annotate annotate friend request status
        :return: annotated field
        """
        return self.annotate(
            friend_request=models.Case(
                models.When(
                    # Check if USER sent friend request
                    models.Q(user__friendrequest_invited__owner=user),
                    then=True,
                ),
                default=False,
                output_field=models.BooleanField(default=False),
            )
        )

    def annotate_full_text_search(self):
        """Full-text search"""
        return self.annotate(
            search=SearchVector(
                "first_name",
                "last_name",
                "user__profilecar__license_plate",
                config="simple",
            )
        )


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


class ProfileGalleryQuerySet(models.QuerySet):
    """ProfileGallery queryset"""

    def by_user(self, user):
        """Show user profile gallery"""
        return self.filter(profile__user=user)

    def by_profile(self, profile):
        """Show user profile gallery"""
        return self.filter(profile=profile)


class ProfileGalleryManager(models.Manager):
    """ProfileGallery manager"""

    def reset_status(self, profile):
        """Reset status is_main"""
        return ProfileGallery.objects.by_profile(profile=profile).by_status(
            switcher=True
        )


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


class FriendRequestQuerySet(models.QuerySet):
    """Custom QuerySet for model FriendRequest"""

    def from_me(self, owner):
        """My requests to add SOMEONE in my friend list"""
        return self.filter(owner=owner)

    def to_me(self, invited):
        """Request to add ME in friend list"""
        return self.filter(invited=invited)

    def common(self, owner, invited):
        """Common request"""
        return self.filter(
            Q(owner=owner, invited=invited)
            | Q(owner=invited, invited=owner) & Q(approved=False)
        )

    def from_me_to_user(self, owner, invited):
        """Return queryset with existed friend request"""
        return self.filter(owner=owner, invited=invited, approved=False)

    def common_by_user(self, user):
        """My requests to add SOMEONE in my friend list"""
        return self.filter(Q(owner=user) | Q(invited=user) & Q(approved=False))

    def approved(self):
        """Approved requests"""
        return self.filter(approved=True)

    def not_approved(self):
        """Not approved requests"""
        return self.filter(approved=False)

    def waiting(self, user, invited):
        """Check whether there is a user request"""
        if self.filter(owner=user, invited=invited, approved=False).exists():
            return True
        else:
            return False


class FriendRequestManager(models.Manager):
    """Custom Manager for FriendRequest model"""

    def make(self, owner, user):
        """Create friend request"""
        obj = self.model(owner=owner, invited=user)
        obj.save()
        obj.send_push_notification()
        return obj


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


class FriendListQuerySet(models.QuerySet):
    """Custom QuerySet for model FriendList"""

    def my_list(self, user):
        """Get user friends"""
        return self.filter(owner=user)

    def common(self, user):
        """Get user friends"""
        return self.filter(Q(owner=user) | Q(friend=user)).filter(
            friend__profile__last_name__isnull=False
        )

    def by_profiles(self, owner, friend):
        """Get user friend by profiles"""
        return self.filter(
            Q(owner__profile=owner) & Q(friend__profile=friend)
            | Q(owner__profile=friend) & Q(friend__profile=owner)
        )

    def by_users(self, owner, friend):
        """Get user friend" by users"""
        return self.filter(
            Q(owner=owner) & Q(friend=friend) | Q(owner=friend) & Q(friend=owner)
        )

    def in_list(self, user):
        """User in someones friendlist"""
        return self.filter(friend=user)

    def are_friends(self, owner, user):
        """Check if user is already a friend"""
        if self.filter(
            Q(owner=owner, friend=user) | Q(owner=user, friend=owner)
        ).exists():
            return True
        else:
            return False


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


class BlackListQuerySet(models.QuerySet):
    """Custom QuerySet for model BlackList"""

    def my_list(self, user):
        """Users in my blacklist"""
        return self.filter(owner=user)

    def in_list(self, user):
        """User in someones blacklist"""
        return self.filter(foe=user)

    def in_my_list(self, owner, foe):
        """User in my blacklist"""
        return self.filter(owner__profile=owner, foe__profile=foe)

    def by_profiles(self, owner, foe):
        """User in my blacklist"""
        return self.filter(owner__profile=owner, foe__profile=foe)

    def common(self, user):
        return self.filter(models.Q(owner=user) | models.Q(foe=user))

    def are_foes(self, owner, user):
        """Check if owner has an enemy"""
        if self.filter(Q(owner=owner, foe=user) | Q(owner=user, foe=owner)).exists():
            return True
        else:
            return False


class BlackListManager(models.Manager):
    """Custom Manager for BlackList model"""

    pass


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
