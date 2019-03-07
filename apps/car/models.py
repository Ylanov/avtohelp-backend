from django.db import models
from utils.mixins import BaseMixin, NameMixin
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db import models as gis_models
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
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


class CarManager(models.Manager):
    """Custom Manager for Car"""
    pass


class CarQuerySet(models.QuerySet):
    """Custom Query for Car"""
    pass


class Car(BaseMixin):
    """Common Car model"""

    mark = models.ForeignKey('CarMark',
                             on_delete=models.CASCADE)
    car_model = models.ForeignKey('CarModel',
                                  on_delete=models.CASCADE)

    class Meta:
        """Meta class"""

        verbose_name = _('Car')
        verbose_name_plural = _('Cars')


class CarService(NameMixin, BaseMixin):
    """Service model"""

    category = models.ForeignKey('CarServiceCategory',
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


class CarServiceCategory(NameMixin, BaseMixin):
    """Service category model"""

    class Meta:
        """Meta model"""

        verbose_name = _('Service category')
        verbose_name_plural = _('Service categories')
