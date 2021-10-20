import logging

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from image_cropping import (
    ImageCropField,
    ImageRatioField,
)

from roadhelpbackend import celery as tasks
from utils.mixins import (
    BaseMixin,
    image_path,
)

# Logging error messages
logger = logging.getLogger("app")


class Newsletter(BaseMixin):
    """Model to new representation."""

    THUMBNAIL_KEY = "news_small"
    title = models.CharField(
        max_length=255, blank=True, default=None, null=True, verbose_name=_("Title")
    )
    text = models.TextField(blank=True, default="", verbose_name=_("Text"))
    short_description = models.CharField(
        max_length=255,
        blank=True,
        default=None,
        null=True,
        verbose_name=_("Short description"),
    )
    publish = models.BooleanField(default=False, verbose_name=_("Publish"))
    push = models.BooleanField(default=False, verbose_name=_("Push notification"))
    as_admin = models.BooleanField(
        default=False, verbose_name=_("Publish as administrator")
    )
    recommendation = models.BooleanField(
        default=False, verbose_name=_("Recommendation")
    )
    publish_date = models.DateTimeField(
        help_text=_("Uses instead created if set"), verbose_name=_("Publish date")
    )
    author = models.ForeignKey(
        "account.User",
        blank=True,
        default=None,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("Author"),
    )
    refused = models.BooleanField(default=False, verbose_name=_("Refused"))

    image = ImageCropField(
        upload_to=image_path,
        null=True,
        blank=True,
        default=None,
        verbose_name=_("Image"),
    )
    cropping = ImageRatioField("image", "600x600", free_crop=True, size_warning=True)

    class Meta:
        """Meta class."""

        verbose_name = _("News")
        verbose_name_plural = _("Newsletter")

    def __str__(self):
        return f"{self.title}"

    def send_push_notification(self):
        """Sent PUSH-notification to all active users"""

        logger.info(
            f"INFO: Send push notification for all active users. News id: {self.id}"
        )
        if settings.USE_CELERY:
            tasks.notify_new_newsletter.delay(self.id)
        else:
            tasks.notify_new_newsletter(self.id)

    def get_image(self, key=None):
        """Get thumbnailed image file."""
        return self.image[key or self.THUMBNAIL_KEY] if self.image else None

    def get_image_url(self, key=None):
        """Get image thumbnail url."""
        return self.get_image(key).url if self.image else None


class NewsletterLike(BaseMixin):

    newsletter = models.ForeignKey(
        "Newsletter", on_delete=models.CASCADE, db_index=True
    )
    owner = models.ForeignKey("account.User", on_delete=models.PROTECT)

    class Meta:
        unique_together = (
            "newsletter",
            "owner",
        )
        verbose_name = _("Newsletter like")
        verbose_name_plural = _("Newsletter likes")

    def save(self, *args, **kwargs):
        super(NewsletterLike, self).save(*args, **kwargs)

    def send_push_notification(self):
        """Sent PUSH-notification to all active users"""

        logger.info(
            f"INFO: Send push notification for author newsletter. NewsletterLike id: {self.id}"
        )
        if settings.USE_CELERY:
            tasks.notify_new_newsletter_like.delay(self.id)
        else:
            tasks.notify_new_newsletter_like(self.id)


class NewsletterComment(BaseMixin):
    """Comments for Newsletter"""

    newsletter = models.ForeignKey(
        "Newsletter", related_name="comments", on_delete=models.CASCADE, db_index=True
    )
    author = models.ForeignKey("account.User", on_delete=models.PROTECT)
    text = models.CharField(
        max_length=1024,
        verbose_name=_("Text comment"),
        blank=False,
        null=False,
        default="",
    )

    class Meta:
        """Meta class"""

        verbose_name = _("Newsletter comment")
        verbose_name_plural = _("Newsletter comments")

    def save(self, *args, **kwargs):
        super(NewsletterComment, self).save(*args, **kwargs)

    def send_push_notification(self):
        """Sent PUSH-notification to all active users"""

        logger.info(
            f"INFO: Send push notification for author newsletter for comment. NewsletterComment id: {self.id}"
        )
        if settings.USE_CELERY:
            tasks.notify_new_newsletter_comment.delay(self.id)
        else:
            tasks.notify_new_newsletter_comment(self.id)


class NewsletterCommentLike(BaseMixin):
    """Comments for Newsletter"""

    comment = models.ForeignKey(
        "NewsletterComment", on_delete=models.CASCADE, db_index=True
    )
    owner = models.ForeignKey("account.User", on_delete=models.PROTECT)

    class Meta:
        """Meta class"""

        unique_together = (
            "comment",
            "owner",
        )

        verbose_name = _("Comment like")
        verbose_name_plural = _("Comment likes")
