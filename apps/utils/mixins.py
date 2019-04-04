import re
import random

from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField
from rest_framework.exceptions import ValidationError
from django.conf import settings
from account import models as account_models


def generate_image_name():
    """Generate code method."""
    return '%06d' % random.randint(0, 999999)


def image_path(instance, filename):
    """Determine avatar path method."""
    filename = '%s.jpeg' % generate_image_name()
    return 'image/%s/%s/%s' % (
        instance._meta.model_name,
        timezone.now().strftime(settings.REST_DATE_FORMAT),
        filename)


class ImageMixin(models.Model):
    """Image field model mixin."""

    THUMBNAIL_KEY = 'gallery'
    image = ThumbnailerImageField(upload_to=image_path,
                                  blank=True, null=True, default=None,
                                  verbose_name=_('Image'))

    class Meta:
        """Meta class."""

        abstract = True

    def get_image(self, key=None):
        """Get thumbnailed image file."""
        return self.image[key or self.THUMBNAIL_KEY] if self.image else None

    def get_image_url(self, key=None):
        """Get image thumbnail url."""
        return self.get_image(key).url if self.image else None

    def image_tag(self):
        """Admin preview tag."""
        if self.image:
            return mark_safe('<img src="%s" />' % self.get_image_url())
        else:
            return None

    def get_image_media_path(self):
        """Get image path with media prefix"""
        return self.image.url

    image_tag.short_description = _('Image')
    image_tag.allow_tags = True


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
