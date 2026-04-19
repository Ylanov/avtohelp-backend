from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.mixins import BaseMixin


class ProfileCar(BaseMixin):
    """User profile car"""

    owner = models.ForeignKey("account.User", on_delete=models.PROTECT)
    car = models.ForeignKey("car.Car", on_delete=models.PROTECT)
    color = models.ForeignKey("car.CarColor", on_delete=models.CASCADE)
    license_plate = models.CharField(
        max_length=255,
        verbose_name=_("License plate"),
        blank=True,
        null=False,
        default="",
    )

    class Meta:
        """Meta class"""

        verbose_name = _("Profile car")
        verbose_name_plural = _("Profile cars")
