import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from rest_framework.routers import SimpleRouter
from solo.models import SingletonModel

# # Logging error messages
logger = logging.getLogger("app")


class UserVerificationConfiguration(SingletonModel):
    """Configuration for User phone verification mode"""

    MODE_CHOICES = (
        ("0", "SMS"),
        ("1", "Phone call"),
    )
    mode = models.CharField(max_length=2, choices=MODE_CHOICES)

    class Meta:
        verbose_name = _("User phone verification configuration")


class BaseSimpleRouter(SimpleRouter):
    def __init__(self):
        self.trailing_slash = "/?"
        super(SimpleRouter, self).__init__()
