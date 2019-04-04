from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from utils.mixins import BaseMixin
from django.contrib.gis.db.models.functions import Distance


class AssistanceRequestQuerySet(models.QuerySet):
    """Custom QuerySet for AssistanceRequest"""

    def by_user(self, user):
        """Filter request by user"""
        return self.filter(user=user)

    def by_status(self, status):
        """Filter by status"""
        return self.filter(status=status)

    def available(self, user):
        """Filter by valid requests"""
        return self.ordinary(user=user).filter(status=AssistanceRequest.AVAILABLE)

    def expired(self):
        """Filter by valid requests"""
        return self.filter(status=AssistanceRequest.EXPIRED)

    def ordinary(self, user):
        """
        Queryset that EXCLUDE requests in which user is owner of blacklist or he is a foe and excluded himself
        :param user:
        :type user: object
        :return: AssistanceRequestQuerySet
        """
        return self.exclude(
            Q(user__blacklist_owner__foe=user) |
            Q(user__blacked_user__owner=user))

    def annotate_distance(self, position):
        """Annotate service distance from position"""
        return self.annotate(distance=Distance('location', position))


class AssistanceRequest(BaseMixin):
    """Assistance request model"""

    EXPIRED = 0
    AVAILABLE = 1
    CANCELED = 2

    STATUS_CHOICES = (
        (AVAILABLE, _('Assistance request is available')),
        (EXPIRED, _('Assistance request was expired')),
        (CANCELED, _('Assistance request was canceled'))
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
                                              default=AVAILABLE, choices=STATUS_CHOICES)

    objects = AssistanceRequestQuerySet.as_manager()

    class Meta:
        """Meta class"""

        verbose_name = _('Assistance request')
        verbose_name_plural = _('Assistance requests')
