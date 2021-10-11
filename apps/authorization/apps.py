from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AuthorizationConfig(AppConfig):
    name = "authorization"
    verbose_name = _("Authorization")
