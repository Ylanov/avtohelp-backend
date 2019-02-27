from django.db import models
from django.contrib.gis.db import models as gis_models
from utils.mixins import BaseMixin
from django.utils.translation import ugettext_lazy as _


# Create your models here.
class AssistanceRequest(BaseMixin):
    """Assistance request model"""

    user = models.ForeignKey('account.User',
                             verbose_name=_('User'),
                             on_delete=models.CASCADE)
    issue = models.CharField(max_length=255,
                             verbose_name=_('Issue'),
                             blank=True, null=True, default=None)
    description = models.TextField(verbose_name=_('Description'))
    location = gis_models.PointField(_('Location'),
                                     blank=True, null=True, default=None)
    car = models.ForeignKey('catalog.Car',
                            verbose_name=_('Car'),
                            on_delete=models.CASCADE)

    class Meta:
        """Meta class"""

        verbose_name = _('Assistance request')
        verbose_name_plural = _('Assistance requests')
