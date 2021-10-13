import logging

from django.db import models

# # Logging error messages
logger = logging.getLogger("app")


class PushNotificationQuerySet(models.QuerySet):
    """PushNotification querysets"""

    pass
