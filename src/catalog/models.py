from django.utils.translation import ugettext_lazy as _

from utils.mixins import BaseMixin, NameMixin


class City(BaseMixin, NameMixin):
    """City model"""

    pass

    class Meta:
        """Meta-class"""

        verbose_name = _("City")
        verbose_name_plural = _("Cities")
