from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CarConfig(AppConfig):
    name = 'car'
    verbose_name = _('Cars')
