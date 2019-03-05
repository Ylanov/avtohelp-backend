from django.db import models
from django.utils.translation import ugettext_lazy as _
from utils.mixins import BaseMixin, NameMixin
from django.contrib.gis.db import models as gis_models
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class Newsletter(BaseMixin):
    """Model to new representation."""

    title = models.CharField(max_length=255, verbose_name=_('Title'))
    text = models.TextField(verbose_name=_('Text'))
    publish = models.BooleanField(default=False, verbose_name=_('Publish'))
    publish_date = models.DateTimeField(help_text=_('Uses instead created if set'),
                                        verbose_name=_('Publish date'))

    class Meta:
        """Meta class."""

        verbose_name = _('News')
        verbose_name_plural = _('Newsletter')


class PushNotification(BaseMixin):
    """Push-notification model"""

    INITIALIZE = 0
    CREATE_REQUEST = 1
    NEW_MESSAGE = 2

    EVENT_CHOICES = (
        (INITIALIZE, _('Initialization')),
        (CREATE_REQUEST, _('Create assistance request')),
        (NEW_MESSAGE, _('New message'))
    )

    title = models.CharField(max_length=255, verbose_name=_('Title'))
    description = models.CharField(max_length=255, verbose_name=_('Description'))
    event = models.PositiveSmallIntegerField(choices=EVENT_CHOICES,
                                             default=INITIALIZE,
                                             verbose_name=_('Event'))
    user = models.ForeignKey('account.User',
                             verbose_name=_('User'),
                             on_delete=models.CASCADE)
    status = models.BooleanField(default=False,
                                 null=True, blank=True,
                                 verbose_name=_('Status'))
    sent_count = models.PositiveIntegerField(
        _('Sent notifications count'),
        default=0,
        blank=True
    )

    class Meta:
        """Meta class"""

        verbose_name = _('Push notification')
        verbose_name_plural = _('Push notifications')


class Service(NameMixin, BaseMixin):
    """Service model"""

    category = models.ForeignKey('catalog.ServiceCategory',
                                 on_delete=models.CASCADE)
    description = models.CharField(max_length=255, verbose_name=_('Description'))
    location = gis_models.PointField(_('Location'))
    phone = PhoneNumberField(
        verbose_name=_('Service contact phone'),
        error_messages={'unique': _("A service with that phone already exists.")},
    )

    class Meta:
        """Meta class"""

        verbose_name = _('Service')
        verbose_name_plural = _('Services')
