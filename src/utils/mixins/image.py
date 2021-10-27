# type: ignore

import random
from os.path import exists

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField


def generate_image_name():
    """Generate code method."""
    return "%06d" % random.randint(0, 999999)


def image_path(instance, filename):
    """Determine avatar path method."""
    filename = "%s.jpeg" % generate_image_name()
    return "image/%s/%s/%s" % (
        instance._meta.model_name,
        timezone.now().strftime(settings.REST_DATE_FORMAT),
        filename,
    )


class ImageMixin(models.Model):
    """Image field model mixin."""

    THUMBNAIL_KEY = "news_small"
    image = ThumbnailerImageField(
        upload_to=image_path,
        null=True,
        blank=True,
        default=None,
        verbose_name=_("Image"),
    )

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

    def get_full_image_url(self, request, thumbnail_key=None):
        """Get full image url"""
        if self.image and exists(self.image.path):
            if thumbnail_key:
                return request.build_absolute_uri(
                    self.image[thumbnail_key].url
                )
            return request.build_absolute_uri(self.image.url)
        else:
            return None

    image_tag.short_description = _("Image")
    image_tag.allow_tags = True
