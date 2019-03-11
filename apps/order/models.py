from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext_lazy as _

from utils.mixins import BaseMixin


class AssistanceRequestManager(models.Manager):
    """Custom manager fro model AssistanceRequest"""
    pass

    # NOTE: If You don't need a manager you can use
    # objects = AssistanceRequestQuerySet.as_manager()
    # So You don't need to define a useless class
    # https://docs.djangoproject.com/en/2.1/topics/db/managers/#create-manager-with-queryset-methods


class AssistanceRequestQuerySet(models.QuerySet):
    """Custom QuerySet for AssistanceRequest"""

    def by_user(self, user):
        """Filter request by user"""
        return self.filter(user=user)

    def by_status(self, status):
        """Filter by status"""
        return self.filter(status=status)


class AssistanceRequest(BaseMixin):
    """Assistance request model"""

    AVAILABLE = 1
    EXPIRED = 0

    STATUS_CHOCIES = (
        (AVAILABLE, _('Assistance request is available')),
        (EXPIRED, _('Assistance request was expired'))
    )

    user = models.ForeignKey('account.User',
                             verbose_name=_('User'),
                             on_delete=models.CASCADE)
    issue = models.CharField(max_length=255,
                             verbose_name=_('Issue'),
                             blank=True, null=True, default=None)
    description = models.TextField(verbose_name=_('Description'))
    location = gis_models.PointField(_('Location'),
                                     blank=True, null=True, default=None)
    status = models.PositiveSmallIntegerField(verbose_name=_('Status'),
                                              default=AVAILABLE, choices=STATUS_CHOCIES)

    objects = AssistanceRequestManager.from_queryset(AssistanceRequestQuerySet)()

    class Meta:
        """Meta class"""

        verbose_name = _('Assistance request')
        verbose_name_plural = _('Assistance requests')
