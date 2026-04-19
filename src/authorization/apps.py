from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuthorizationConfig(AppConfig):
    name = "authorization"
    verbose_name = _("Authorization")
