from django.db import models
from django.utils.translation import gettext_lazy as _
from fcm_django import models as fcm_models

from ..managers import FCMDeviceManager


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
