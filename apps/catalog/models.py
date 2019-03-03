from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext_lazy as _

from utils.mixins import BaseMixin, NameMixin
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class City(BaseMixin, NameMixin):
    """City model"""
    pass

    class Meta:
        """Meta-class"""

        verbose_name = _('City')
        verbose_name_plural = _('Cities')


class CarMark(BaseMixin, NameMixin):
    """Car brands model"""
    pass

    class Meta:
        """Meta model"""

        verbose_name = _('Car brand')
        verbose_name_plural = _('Car brands')


class CarModel(BaseMixin, NameMixin):
    """Models for car models"""

    mark = models.ForeignKey('CarMark', on_delete=models.CASCADE)

    class Meta:
        """Meta class"""

        verbose_name = _('Car model')
        verbose_name_plural = _('Car models')


class CarColor(NameMixin, BaseMixin):
    """Car color model"""

    class Meta:
        """Meta class"""

    verbose_name = _('Car color')
    verbose_name_plural = _('Car colors')


class ServiceCategory(NameMixin, BaseMixin):
    """Service category model"""

    class Meta:
        """Meta model"""

        verbose_name = _('Service category')
        verbose_name_plural = _('Service categories')


class Service(NameMixin, BaseMixin):
    """Service model"""

    category = models.ForeignKey('ServiceCategory',
                                 on_delete=models.CASCADE)
    description = models.CharField(max_length=255, verbose_name=_('Description'))
    location = gis_models.PointField(_('Location'))
    phone = PhoneNumberField(
        verbose_name=_('Service contact phone'), unique=True,
        error_messages={'unique': _("A service with that phone already exists.")},
    )
    # FIXIT: убери unique, это справочник. + один и тот же номер может быть у нескольких компаний
    # особенно это касается авто сервисов, шиномонтажка. мойка и чет еще, сервиса 3,  телефон 1

    class Meta:
        """Meta class"""

        verbose_name = _('Service')
        verbose_name_plural = _('Services')
