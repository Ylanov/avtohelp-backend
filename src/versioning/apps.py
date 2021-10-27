from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class VersioningConfig(AppConfig):
    name = "versioning"
    verbose_name = _("Versioning")
