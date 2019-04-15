"""Documentation app config."""
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DocumentationAPIConfig(AppConfig):
    """Config class itself."""

    name = 'documentation'
    verbose_name = _('Documentation')
