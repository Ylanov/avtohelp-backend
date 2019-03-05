from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from apps.utils.mixins import BaseMixin, NameMixin


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

