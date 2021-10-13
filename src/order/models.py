from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db import (
    models,
    transaction,
)
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from base.models import PushNotificationConfiguration
from roadhelpbackend import celery as tasks
from utils.mixins import (
    BaseMixin,
    ImageMixin,
)


class AssistanceRequestQuerySet(models.QuerySet):
    """Custom QuerySet for AssistanceRequest"""

    def by_user(self, user):
        """Filter request by user"""
        return self.filter(user=user)

    def by_status(self, status):
        """Filter by status"""
        return self.filter(status=status)

    def available(self, user):
        """Filter by valid requests"""
        return self.ordinary(user=user).filter(status=AssistanceRequest.AVAILABLE)

    def expired(self):
        """Filter by valid requests"""
        return self.filter(status=AssistanceRequest.EXPIRED)

    def ordinary(self, user):
        """
        Queryset that EXCLUDE requests in which user is owner of blacklist or he is a foe and excluded himself
        :param user:
        :type user: object
        :return: AssistanceRequestQuerySet
        """
        return self.exclude(
            Q(user__blacklist_owner__foe=user) | Q(user__blacked_user__owner=user)
        )

    def annotate_distance(
        self,
        raw_coordinates: list = None,
        latitude: float = None,
        longitude: float = None,
        point: Point = None,
    ):
        """
        Annotate service distance from position
        raw_coordinates can contain -
        - latitude (index 0),
        - longitude (index 1),

        point parameter is Point object
        """
        if raw_coordinates:
            x, y = raw_coordinates.split(",")[0], raw_coordinates.split(",")[1]
            return self.annotate(
                distance=Distance("location", Point(float(x), float(y), srid=4326))
            )
        elif latitude and longitude:
            return self.annotate(
                distance=Distance(
                    "location", Point(float(latitude), float(longitude), srid=4326)
                )
            )
        elif point:
            return self.annotate(distance=Distance("location", point, srid=4326))
        else:
            return self

    def annotate_owner_status(self, user):

        return self.annotate(
            is_owner=models.Case(
                models.When(user=user, then=True),
                output_field=models.BooleanField(default=False),
                default=False,
            )
        )


class AssistanceRequestManager(models.Manager):
    """Manager for AssistanceRequest model"""

    def make(self, **kwargs):
        """Make new assistance request"""
        obj = self.model(**kwargs)
        obj.save()
        obj.send_push_notification()
        return obj


class AssistanceRequest(BaseMixin, ImageMixin):
    """Assistance request model"""

    EXPIRED = 0
    AVAILABLE = 1
    CANCELED = 2

    STATUS_CHOICES = (
        (AVAILABLE, _("Assistance request is available")),
        (EXPIRED, _("Assistance request was expired")),
        (CANCELED, _("Assistance request was canceled")),
    )

    user = models.ForeignKey(
        "account.User", verbose_name=_("User"), on_delete=models.CASCADE
    )
    issue = models.CharField(
        max_length=255, verbose_name=_("Issue"), blank=True, null=True, default=None
    )
    description = models.TextField(verbose_name=_("Description"))
    location = gis_models.PointField(_("Location"), blank=True, null=True, default=None)
    status = models.PositiveSmallIntegerField(
        verbose_name=_("Status"), default=AVAILABLE, choices=STATUS_CHOICES
    )
    contact_phone = PhoneNumberField(
        verbose_name=_("User contact phone"), blank=True, null=True, default=None
    )
    text_address = models.CharField(
        max_length=255,
        verbose_name=_("Text address"),
        blank=True,
        null=True,
        default=None,
    )

    objects = AssistanceRequestManager.from_queryset(AssistanceRequestQuerySet)()

    class Meta:
        """Meta class"""

        verbose_name = _("Assistance request")
        verbose_name_plural = _("Assistance requests")

    def send_push_notification(self):
        """Notify all users about new assistance request"""
        if settings.USE_CELERY:
            transaction.on_commit(
                lambda: tasks.notify_assistance_request.delay(self.id)
            )
        else:
            transaction.on_commit(lambda: tasks.notify_assistance_request(self.id))


class AssistanceRequestUserReadManager(models.Manager):
    """Manager for AssistanceRequest model"""

    def make(self, **kwargs):
        """Make new assistance request"""
        obj = self.model(**kwargs)
        obj.save()
        return obj


class AssistanceRequestUserRead(BaseMixin):
    """Assistance request User read model"""

    request = models.ForeignKey(
        "order.AssistanceRequest",
        verbose_name=_("Order"),
        related_name="assistance_request_user_read",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        "account.User", verbose_name=_("User"), on_delete=models.CASCADE
    )
    objects = AssistanceRequestUserReadManager()
