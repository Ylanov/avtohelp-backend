from colorful.fields import RGBColorField
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from utils.mixins import (
    BaseMixin,
    ImageMixin,
    NameMixin,
)

from .managers import CarServiceManager
from .query_set import CarServiceQuerySet


class CarMark(BaseMixin, NameMixin):
    """Car brands model"""

    class Meta:
        """Meta model"""

        verbose_name = _("Car brand")
        verbose_name_plural = _("Car brands")


class CarModel(BaseMixin, NameMixin):
    """Models for car models"""

    mark = models.ForeignKey("CarMark", on_delete=models.CASCADE)

    class Meta:
        """Meta class"""

        verbose_name = _("Car model")
        verbose_name_plural = _("Car models")


class CarColor(NameMixin, BaseMixin):
    """Car color model"""

    hex_color = RGBColorField(blank=True, default=None, null=True)

    class Meta:
        """Meta class"""

    verbose_name = _("Car color")
    verbose_name_plural = _("Car colors")


class Car(BaseMixin):
    """Common Car model"""

    mark = models.ForeignKey("CarMark", on_delete=models.CASCADE)
    car_model = models.ForeignKey("CarModel", on_delete=models.CASCADE)

    class Meta:
        """Meta class"""

        verbose_name = _("Car")
        verbose_name_plural = _("Cars")


class CarService(NameMixin, BaseMixin):
    """Service model"""

    category = models.ForeignKey("CarServiceCategory", on_delete=models.CASCADE)
    description = models.CharField(max_length=255, verbose_name=_("Description"))
    location = gis_models.PointField(_("Location"))
    phone = PhoneNumberField(
        verbose_name=_("Service contact phone"),
        error_messages={"unique": _("A service with that phone already exists.")},
    )

    objects = CarServiceManager.from_queryset(CarServiceQuerySet)()

    class Meta:
        """Meta class"""

        verbose_name = _("Service")
        verbose_name_plural = _("Services")


class CarServiceCategory(NameMixin, BaseMixin, ImageMixin):
    """Service category model"""

    class Meta:
        """Meta model"""

        verbose_name = _("Service category")
        verbose_name_plural = _("Service categories")
