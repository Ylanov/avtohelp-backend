from django.utils.translation import ugettext_lazy as _

from apps.utils.mixins import BaseMixin, NameMixin


# Create your models here.
class City(BaseMixin, NameMixin):
    """City model"""
    pass

    class Meta:
        """Meta-class"""

        verbose_name = _('City')
        verbose_name_plural = _('Cities')


