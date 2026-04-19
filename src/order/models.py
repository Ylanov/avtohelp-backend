# type: ignore

from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.db.models import Manager as GeoManager
from django.db import (
    models,
    transaction,
)
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from utils.mixins import (
    BaseMixin,
    ImageMixin,
)

from .choices import (
    AVAILABLE,
    STATUS_CHOICES,
)
from .managers import (
    AssistanceRequestManager,
    AssistanceRequestUserReadManager,
)
from .query_sets import AssistanceRequestQuerySet


class AssistanceRequest(BaseMixin, ImageMixin):
    """Assistance request model"""

    user = models.ForeignKey(
        "account.User",
        verbose_name=_("User"),
        on_delete=models.CASCADE,
    )
    issue = models.CharField(
        max_length=255,
        verbose_name=_("Issue"),
        blank=True,
        null=True,
        default=None,
    )
    description = models.TextField(verbose_name=_("Description"))
    location = gis_models.PointField(
        _("Location"), blank=True, null=True, default=None
    )

    lng = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    lat = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)

    status = models.PositiveSmallIntegerField(
        verbose_name=_("Status"),
        default=AVAILABLE,
        choices=STATUS_CHOICES,
    )
    contact_phone = PhoneNumberField(
        verbose_name=_("User contact phone"),
        blank=True,
        null=True,
        default=None,
    )
    text_address = models.CharField(
        max_length=255,
        verbose_name=_("Text address"),
        blank=True,
        null=True,
        default=None,
    )

    objects = AssistanceRequestManager.from_queryset(
        AssistanceRequestQuerySet
    )()

    gis = GeoManager()

    class Meta:
        indexes = [
            models.Index(fields=["user", "lng", "lat", "status"], name="order_req_geo_status_idx"),
        ]
        verbose_name = _("Assistance request")
        verbose_name_plural = _("Assistance requests")

    def send_push_notification(self):
        from .tasks import notify_assistance_request
        if settings.USE_CELERY:

            transaction.on_commit(
                lambda: notify_assistance_request.delay(self.id)
            )
        else:
            transaction.on_commit(
                lambda: notify_assistance_request(self.id)
            )


class AssistanceRequestUserRead(BaseMixin):

    request = models.ForeignKey(
        "order.AssistanceRequest",
        verbose_name=_("Order"),
        related_name="assistance_request_user_read",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        "account.User",
        verbose_name=_("User"),
        on_delete=models.CASCADE,
    )
    objects = AssistanceRequestUserReadManager()
