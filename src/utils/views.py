from rest_framework.permissions import AllowAny

from authorization import models as auth_models
from base import models as base_models


class AuthorizationViewMixin(object):
    """Mixin for authorization views"""

    permission_classes = (AllowAny,)
    queryset = auth_models.SMSCode.objects.all()


class NotificationViewMixin(object):
    """Mixin for notification views"""

    queryset = base_models.PushNotification.objects.all()
