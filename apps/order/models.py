from django.db import models
from django.contrib.gis.db import models as gis_models
from utils.mixins import BaseMixin
from django.utils.translation import ugettext_lazy as _


"""
ASSISTANCE REQUEST
"""


class AssistanceRequestManager(models.Manager):
    """Custom manager fro model AssistanceRequest"""
    pass


class AssistanceRequestQuerySet(models.QuerySet):
    """Custom QuerySet for AssistanceRequest"""

    def by_user(self, user):
        """Filter request by user"""
        return self.filter(user=user)


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
    car = models.ForeignKey('userprofile.Car',
                            verbose_name=_('Car'),
                            on_delete=models.CASCADE)

    objects = AssistanceRequestManager.from_queryset(AssistanceRequestQuerySet)()

    class Meta:
        """Meta class"""

        verbose_name = _('Assistance request')
        verbose_name_plural = _('Assistance requests')
