# type: ignore

import datetime
import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel

from utils.mixins import BaseMixin

from ..managers import PushNotificationManager
from ..query_set import PushNotificationQuerySet

#   Logging error messages
logger = logging.getLogger("app")


class PushNotification(BaseMixin):
    """Push-notification model"""

    INITIALIZE = 0
    CREATE_REQUEST = 1
    NEW_MESSAGE = 2
    FRIEND_REQUEST = 3
    NEW_NEWSLETTER = 4
    NEW_NEWSLETTER_LIKE = 5
    NEW_NEWSLETTER_COMMENT = 6

    EVENT_CHOICES = (
        (INITIALIZE, _("Initialization")),
        (CREATE_REQUEST, _("Create assistance request")),
        (NEW_MESSAGE, _("New message")),
        (FRIEND_REQUEST, _("Friend request")),
        (NEW_NEWSLETTER, _("Newsletter")),
        (NEW_NEWSLETTER_LIKE, _("Newsletter like")),
        (NEW_NEWSLETTER_COMMENT, _("New newsletter comment")),
    )

    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.CharField(
        max_length=255, verbose_name=_("Description")
    )
    event = models.PositiveSmallIntegerField(
        choices=EVENT_CHOICES,
        default=INITIALIZE,
        verbose_name=_("Event"),
    )
    user = models.ForeignKey(
        "account.User",
        verbose_name=_("User"),
        on_delete=models.CASCADE,
    )
    status = models.BooleanField(
        default=False, null=True, blank=True, verbose_name=_("Status")
    )
    sent_count = models.PositiveIntegerField(
        _("Sent notifications count"), default=0, blank=True
    )

    objects = PushNotificationManager.from_queryset(PushNotificationQuerySet)()

    class Meta:
        """Meta class"""

        verbose_name = _("Push notification")
        verbose_name_plural = _("Push notifications")

    def get_push_dict(self, **kwargs):
        """Make dict object, for push notification."""
        result = dict()
        result.update(
            {
                "title": "Автопомощь на дороге",
                "body": str(self.description),
                "data": {
                    "data": {
                        "event_id": self.event,
                        "title": str(self.title),
                        "body": str(self.description),
                        **kwargs,
                    }
                },
                "sound": "default",
                "icon": "ic_launcher",
            }
        )
        return result


class PushNotificationSchedule(models.Model):
    """Push-notification schedule"""

    time = models.TimeField(verbose_name=_("time"))

    class Meta:
        verbose_name = _("Push-notification schedule")
        verbose_name_plural = _("Push-notification schedules")
        ordering = ("time",)

    def __str__(self):
        """String representation"""
        return f"{self.time.isoformat()}"


class PushNotificationConfiguration(SingletonModel):
    """Configuration for sending Push-notifications"""

    radius = models.FloatField(
        blank=True,
        null=True,
        default=5000,
        verbose_name=_("Radius"),
        help_text=_("Radius in meters"),
    )
    geo_position_lifetime = models.TimeField(
        blank=True,
        null=True,
        default=datetime.time(hour=6),
        verbose_name=_("Geo position lifetime"),
        help_text=_("Profile geo-position lifetime"),
    )
    notification_schedule = models.ManyToManyField(
        PushNotificationSchedule,
        verbose_name=_("Notification schedule"),
    )

    class Meta:
        verbose_name = _("Push notification configuration")
