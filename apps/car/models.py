from django.db import models
from utils.mixins import BaseMixin, NameMixin, ImageMixin
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db import models as gis_models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.gis.db.models.functions import Distance
from colorful.fields import RGBColorField
from django.contrib.postgres.search import SearchVector


class CarMarkQuerySet(models.QuerySet):
    """QuerySet for model CarMark"""

    def annotate_full_search(self, *args, **kwargs):
        return self.annotate(
            search=SearchVector(
                'name',
                'carmodel__name',
            ),
        )


class CarMark(BaseMixin, NameMixin):
    """Car brands model"""

    objects = CarMarkQuerySet.as_manager()

    class Meta:
        """Meta model"""

        verbose_name = _('Car brand')
        verbose_name_plural = _('Car brands')


class CarModelQuerySet(models.QuerySet):
    """QuerySet for model CarModel"""

    def annotate_full_search(self, *args, **kwargs):
        return self.annotate(
            search=SearchVector(
                'name',
                'mark__name',
            ),
        )


class CarModel(BaseMixin, NameMixin):
    """Models for car models"""

    mark = models.ForeignKey('CarMark', on_delete=models.CASCADE)
    objects = CarModelQuerySet.as_manager()

    class Meta:
        """Meta class"""

        verbose_name = _('Car model')
        verbose_name_plural = _('Car models')


class CarColor(NameMixin, BaseMixin):
    """Car color model"""

    hex_color = RGBColorField(blank=True,
                              default=None,
                              null=True)

    class Meta:
        """Meta class"""

    verbose_name = _('Car color')
    verbose_name_plural = _('Car colors')


class CarQuerySet(models.QuerySet):
    """Custom Query for Car"""

    def annotate_full_search(self, *args, **kwargs):
        return self.annotate(
            search=SearchVector(
                'mark__name',
                'car_model__name',
            ),
        )


class Car(BaseMixin):
    """Common Car model"""

    mark = models.ForeignKey('CarMark',
                             on_delete=models.CASCADE)
    car_model = models.ForeignKey('CarModel',
                                  on_delete=models.CASCADE)

    objects = CarQuerySet.as_manager()

    class Meta:
        """Meta class"""

        verbose_name = _('Car')
        verbose_name_plural = _('Cars')


class CarServiceManager(models.Manager):
    """Manager for model CarServiceManager"""
    pass


class CarServiceQuerySet(models.QuerySet):
    """QuerySet for model CarService"""

    def annotate_distance(self, position):
        """Annotate service distance from position"""
        return self.annotate(distance=Distance('location', position))

    def annotate_icon_exists(self):
        """Annotate flag that return True if service category icon is exists"""
        return self.annotate(
            icon_exists=models.Case(
                models.When(category__image__isnull=False,
                            then=True),
                output_field=models.BooleanField(default=False),
                default=False
            )
        )


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

    objects = CarServiceManager.from_queryset(CarServiceQuerySet)()

    class Meta:
        """Meta class"""

        verbose_name = _('Service')
        verbose_name_plural = _('Services')


class CarServiceCategory(NameMixin, BaseMixin, ImageMixin):
    """Service category model"""

    class Meta:
        """Meta model"""

        verbose_name = _('Service category')
        verbose_name_plural = _('Service categories')
