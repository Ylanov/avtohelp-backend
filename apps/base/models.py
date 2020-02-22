import datetime
import logging

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel
from rest_framework.routers import SimpleRouter

from account import models as account_models
from utils.mixins import BaseMixin, ImageMixin, image_path
from project import celery as tasks
from image_cropping import ImageCropField, ImageRatioField

# # Logging error messages
logger = logging.getLogger('app')

class Newsletter(BaseMixin):
    """Model to new representation."""

    THUMBNAIL_KEY = 'news_small'
    title = models.CharField(max_length=255, blank=True, default=None, null=True, verbose_name=_('Title'))
    text = models.TextField(blank=True, default='', verbose_name=_('Text'))
    short_description = models.CharField(max_length=255,
                                         blank=True, default=None, null=True,
                                         verbose_name=_('Short description'))
    publish = models.BooleanField(default=False, verbose_name=_('Publish'))
    push = models.BooleanField(default=False, verbose_name=_('Push notification'))
    recommendation = models.BooleanField(default=False, verbose_name=_('Recommendation'))
    publish_date = models.DateTimeField(help_text=_('Uses instead created if set'),
                                        verbose_name=_('Publish date'))
    author = models.ForeignKey('account.User',  blank=True, default=None, null=True,
                                        on_delete=models.PROTECT,
                                        verbose_name=_('Author'))
    refused = models.BooleanField(default=False, verbose_name=_('Refused'))

    image = ImageCropField(upload_to=image_path, null=True, blank=True, default=None, verbose_name=_('Image'))
    cropping = ImageRatioField('image', '600x600', free_crop=True, size_warning=True)

    class Meta:
        """Meta class."""

        verbose_name = _('News')
        verbose_name_plural = _('Newsletter')

    def send_push_notification(self):
        """Sent PUSH-notification to all active users"""

        logger.info(f'INFO: Send push notification for all active users. News id: {self.id}')
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
    """Comments for Newsletter"""
    newsletter = models.ForeignKey('Newsletter', on_delete=models.CASCADE)
    owner = models.ForeignKey('account.User', on_delete=models.PROTECT)

    class Meta:
        """Meta class"""

        verbose_name = _('Newsletter like')
        verbose_name_plural = _('Newsletter likes')

    def save(self, *args, **kwargs):
        super(NewsletterLike, self).save(*args, **kwargs)
        # self.send_push_notification()

    def send_push_notification(self):
        """Sent PUSH-notification to all active users"""

        logger.info(f'INFO: Send push notification for author newsletter. NewsletterLike id: {self.id}')
        if settings.USE_CELERY:
            tasks.notify_new_newsletter_like.delay(self.id)
        else:
            tasks.notify_new_newsletter_like(self.id)

class NewsletterComment(BaseMixin):
    """Comments for Newsletter"""
    newsletter = models.ForeignKey('Newsletter', related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey('account.User', on_delete=models.PROTECT)
    text = models.CharField(max_length=1024,
                                     verbose_name=_('Text comment'),
                                     blank=False, null=False, default='')
    class Meta:
        """Meta class"""

        verbose_name = _('Newsletter comment')
        verbose_name_plural = _('Newsletter comments')

    def save(self, *args, **kwargs):
        super(NewsletterComment, self).save(*args, **kwargs)
        # self.send_push_notification()

    def send_push_notification(self):
        """Sent PUSH-notification to all active users"""

        logger.info(f'INFO: Send push notification for author newsletter for comment. NewsletterComment id: {self.id}')
        if settings.USE_CELERY:
            tasks.notify_new_newsletter_comment.delay(self.id)
        else:
            tasks.notify_new_newsletter_comment(self.id)

class NewsletterCommentLike(BaseMixin):
    """Comments for Newsletter"""
    comment = models.ForeignKey('NewsletterComment', on_delete=models.CASCADE)
    owner = models.ForeignKey('account.User', on_delete=models.PROTECT)

    class Meta:
        """Meta class"""

        verbose_name = _('Comment like')
        verbose_name_plural = _('Comment likes')

class PushNotificationManager(models.Manager):
    """PushNotification manager"""

    def make_friend_request_notification(self, user: (str, int, object)) -> object:
        """Make common notification for friend request"""
        user_id = user.id if isinstance(user, account_models.User) else user
        if account_models.User.objects.filter(id=user_id).exists():
            obj = self.model(
                user_id=user_id,
                title=_('New friend request'),
                description=_('A new friend request has been received'),
                event=self.model.FRIEND_REQUEST
            )
            obj.save()
            return obj

    def make_assistance_request_notification(self, user: (str, int, object)) -> object:
        """Make common notification for assistance request"""
        user_id = user.id if isinstance(user, account_models.User) else user
        if account_models.User.objects.filter(id=user_id).exists():
            obj = self.model(
                user_id=user_id,
                title=_('New assistance request'),
                description=_('New assistance request was published'),
                event=self.model.CREATE_REQUEST
            )
            obj.save()
            return obj

    def make_new_message_notification(self, user: (str, int, object), sender: (str, int, object)) -> object:
        """Make common notification for new chat message"""
        if not isinstance(user, account_models.User):
            user_qs = account_models.User.objects.filter(id=user)
            if user_qs.exists():
                user = user_qs.first()
            else:
                return None

        if not isinstance(sender, account_models.User):
            sender_qs = account_models.User.objects.filter(id=sender)
            if sender_qs.exists():
                sender = sender_qs.first()
            else:
                return None

        obj = self.model(
            user=user,
            title=_('New message from chat'),
            description=_('User %s wrote a message') % sender.get_full_name,
            event=self.model.NEW_MESSAGE
        )
        obj.save()
        return obj

    def make_new_newsletter_notification(self, user: (str, int, object), newsletter: (str, int, object)) -> object:
        """Make common notification for new newsletter"""
        user_id = user.id if isinstance(user, account_models.User) else user

        if not isinstance(newsletter, Newsletter):
            newsletter_qs = Newsletter.objects.filter(id=newsletter)
            if newsletter_qs.exists():
                newsletter = newsletter_qs.first()
            else:
                return None

        if account_models.User.objects.filter(id=user_id).exists():
            obj = self.model(
                user_id=user_id,
                title=_('News'),
                description=newsletter.title,
                event=self.model.NEW_NEWSLETTER
            )
            obj.save()
            return obj

    def make_newsletter_like_notification(self, user: (str, int, object), initiator: (str, int, object)) -> object:
        """Make common notification for newsletter like"""
        user_id = user.id if isinstance(user, account_models.User) else user

        if not isinstance(initiator, account_models.User):
            initiator_qs = account_models.User.objects.filter(id=initiator)
            if initiator_qs.exists():
                initiator = initiator_qs.first()
            else:
                return None

        if account_models.User.objects.filter(id=user_id).exists():
            obj = self.model(
                user_id=user_id,
                title=_('Like'),
                description=_('User %s liked your newsletter') % initiator.get_full_name,
                event=self.model.NEW_NEWSLETTER_LIKE
            )
            obj.save()
            return obj

    def make_newsletter_comment_notification(self, user: (str, int, object), initiator: (str, int, object)) -> object:
        """Make common notification for newsletter comment"""
        user_id = user.id if isinstance(user, account_models.User) else user

        if not isinstance(initiator, account_models.User):
            initiator_qs = account_models.User.objects.filter(id=initiator)
            if initiator_qs.exists():
                initiator = initiator_qs.first()
            else:
                return None

        if account_models.User.objects.filter(id=user_id).exists():
            obj = self.model(
                user_id=user_id,
                title=_('New comment'),
                description=_('User %s comment your newsletter') % initiator.get_full_name,
                event=self.model.NEW_NEWSLETTER_COMMENT
            )
            obj.save()
            return obj



class PushNotificationQuerySet(models.QuerySet):
    """PushNotification querysets"""
    pass


class PushNotification(BaseMixin):
    """Push-notification model"""

    INITIALIZE = 0
    CREATE_REQUEST = 1
    NEW_MESSAGE = 2
    FRIEND_REQUEST = 3
    NEW_NEWSLETTER = 4
    NEW_NEWSLETTER_LIKE = 5
    NEW_NEWSLETTER_COMMENT = 6

    EVENT_CHOICES = (
        (INITIALIZE, _('Initialization')),
        (CREATE_REQUEST, _('Create assistance request')),
        (NEW_MESSAGE, _('New message')),
        (FRIEND_REQUEST, _('Friend request')),
        (NEW_NEWSLETTER, _('Newsletter')),
        (NEW_NEWSLETTER_LIKE, _('Newsletter like')),
        (NEW_NEWSLETTER_COMMENT, _('New newsletter comment'))
    )

    title = models.CharField(max_length=255, verbose_name=_('Title'))
    description = models.CharField(max_length=255, verbose_name=_('Description'))
    event = models.PositiveSmallIntegerField(choices=EVENT_CHOICES,
                                             default=INITIALIZE,
                                             verbose_name=_('Event'))
    user = models.ForeignKey('account.User',
                             verbose_name=_('User'),
                             on_delete=models.CASCADE)
    status = models.BooleanField(default=False,
                                 null=True, blank=True,
                                 verbose_name=_('Status'))
    sent_count = models.PositiveIntegerField(
        _('Sent notifications count'),
        default=0,
        blank=True
    )

    objects = PushNotificationManager.from_queryset(PushNotificationQuerySet)()

    class Meta:
        """Meta class"""

        verbose_name = _('Push notification')
        verbose_name_plural = _('Push notifications')

    def get_push_dict(self, **kwargs):
        """Make dict object, for push notification."""
        result = dict()
        result.update({
            'title': 'Автопомощь на дороге',
            'body': str(self.description),
            'data': {
                'data': {
                    'event_id': self.event,
                    'title': str(self.title),
                    'body': str(self.description),
                    **kwargs
                }
            },
            'sound': 'default',
            'icon': 'ic_launcher',
        })
        return result


class PushNotificationSchedule(models.Model):
    """Push-notification schedule"""

    time = models.TimeField(verbose_name=_("time"))

    class Meta:
        verbose_name = _('Push-notification schedule')
        verbose_name_plural = _('Push-notification schedules')
        ordering = ('time', )

    def __str__(self):
        """String representation"""
        return f'{self.time.isoformat()}'


class PushNotificationConfiguration(SingletonModel):
    """Configuration for sending Push-notifications"""

    radius = models.FloatField(blank=True, null=True, default=5000,
                               verbose_name=_('Radius'),
                               help_text=_('Radius in meters'))
    geo_position_lifetime = models.TimeField(blank=True, null=True,
                                             default=datetime.time(hour=6),
                                             verbose_name=_('Geo position lifetime'),
                                             help_text=_('Profile geo-position lifetime'))
    notification_schedule = models.ManyToManyField(PushNotificationSchedule,
                                                   verbose_name=_('Notification schedule'))

    class Meta:
        verbose_name = _("Push notification configuration")


class UserVerificationConfiguration(SingletonModel):
    """Configuration for User phone verification mode"""

    MODE_CHOICES = (
        ("0" , 'SMS'),
        ("1" , 'Phone call'),
    )
    mode = models.CharField(max_length=2, choices=MODE_CHOICES)
    

    class Meta:
        verbose_name = _("User phone verification configuration")


class BaseSimpleRouter(SimpleRouter):
    def __init__(self):
        self.trailing_slash = '/?'
        super(SimpleRouter, self).__init__()

