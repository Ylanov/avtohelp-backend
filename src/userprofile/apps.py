from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class UserprofileConfig(AppConfig):
    name = "userprofile"
    verbose_name = _("User profile")

    def ready(self):
        from . import signals  # noqa
