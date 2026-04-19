from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class BaseMixin(models.Model):
    """Base mixin model."""

    created = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name=_("Date created"),
    )
    modified = models.DateTimeField(
        auto_now=True, verbose_name=_("Date updated")
    )

    class Meta:
        """Meta-class"""

        abstract = True


class NameMixin(models.Model):
    """Name field model mixin."""

    name = models.CharField(max_length=255, verbose_name=_("Name"))

    class Meta:
        """Meta class."""

        abstract = True

    def __str__(self):
        """String method."""
        return self.name
