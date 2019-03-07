import re

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError
from utils.api_exceptions import CityNotFound

from account import models as account_models
from catalog import models as catalog_models


class BaseMixin(models.Model):
    """Base mixin model."""

    created = models.DateTimeField(default=timezone.now, editable=False,
                                   verbose_name=_('Date created'))
    modified = models.DateTimeField(auto_now=True,
                                    verbose_name=_('Date updated'))

    class Meta:
        """Meta-class"""

        abstract = True


class NameMixin(models.Model):
    """Name field model mixin."""

    name = models.CharField(max_length=255, verbose_name=_('Name'))

    class Meta:
        """Meta class."""

        abstract = True

    def __str__(self):
        """String method."""
        return self.name


class AuthorizationMixin(object):
    """Mixin for serializer AuthorizationSerializer"""

    def validate_phone(self, value):
        """Validate phone"""
        qs = account_models.User.objects.filter(phone=value.as_e164)
        if not qs.exists():
            raise ValidationError(detail={
                'detail': _('User with this phone number is not found')
            })
        return value

    def validate_code(self, value):
        """Validate code method."""
        pattern = r'[0-9]{4}'
        if not re.fullmatch(pattern, str(value)):
            raise ValidationError(_('Invalid code'))
        return value
