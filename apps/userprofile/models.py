from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from easy_thumbnails.fields import ThumbnailerImageField

from utils import methods
from utils.mixins import BaseMixin


class Car(BaseMixin):
    """Car model"""

    user = models.ForeignKey('account.User', on_delete=models.PROTECT)

    mark = models.ForeignKey('catalog.CarMark',
                             on_delete=models.CASCADE)
    model = models.ForeignKey('catalog.CarModel',
                              on_delete=models.CASCADE)
    color = models.ForeignKey('catalog.CarColor',
                              on_delete=models.CASCADE)
    license_plate = models.CharField(max_length=255,
                                     verbose_name=_('License plate'))

    class Meta:
        """Meta class"""

        verbose_name = _('Car')
        verbose_name_plural = _('Cars')


class Profile(BaseMixin):
    """Profile model"""

    user = models.OneToOneField('account.User', on_delete=models.PROTECT)
    first_name = models.CharField(max_length=255, null=True, blank=True,
                                  default=None, verbose_name=_('Name'))
    last_name = models.CharField(max_length=255, null=True, blank=True,
                                 default=None, verbose_name=_('Last name'))
    middle_name = models.CharField(max_length=255, null=True, blank=True,
                                   default=None, verbose_name=_('Middle name'))
    avatar = ThumbnailerImageField(upload_to=methods.image_path, blank=True,
                                   null=True, default=None,
                                   verbose_name=_('Avatar'))
    city = models.ForeignKey('catalog.City',
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True,
                             default=None)
    location = gis_models.PointField(_('Location'),
                                     blank=True, null=True, default=None)
    friends = models.OneToOneField('account.User',
                                   related_name='friends',
                                   verbose_name=_('Friend list'),
                                   blank=True, null=True, default=None,
                                   on_delete=models.CASCADE)
    blacklist = models.OneToOneField('account.User',
                                     related_name='blacklist',
                                     verbose_name=_('Black list'),
                                     blank=True, null=True, default=None,
                                     on_delete=models.CASCADE)

    class Meta:
        """Meta class."""

        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')


class FriendRequest(BaseMixin):
    """Friend request model"""

    user = models.ForeignKey('account.User',
                             verbose_name=_('Owner'),
                             on_delete=models.CASCADE)
    invited = models.ForeignKey('account.User',
                                verbose_name=_('Invited user'),
                                related_name='friendrequest_invited', on_delete=models.CASCADE)
    approved = models.BooleanField(default=False,
                                   verbose_name=_('Status'))

    class Meta:
        """Meta-class"""
        verbose_name = _('Friend request')
        verbose_name_plural = _('Friend request')


class FriendList(BaseMixin):
    """Friend-list model"""

    owner = models.ForeignKey('account.User',
                              verbose_name=_('Owner'),
                              related_name='friendlist_owner', on_delete=models.CASCADE,)
    friend = models.ForeignKey('account.User',
                               verbose_name=_('Friend'),
                               related_name='friendlist_user',
                               blank=True, null=True, default=None, on_delete=models.CASCADE)
    request = models.ForeignKey('FriendRequest',
                                verbose_name=_('Request'),
                                related_name='friendlist_request',
                                blank=True, null=True, default=None, on_delete=models.CASCADE)

    class Meta:
        """Meta-class"""
        verbose_name = _('Friend list')
        verbose_name_plural = _('Friend lists')


class BlackList(BaseMixin):
    """Black-list model"""

    owner = models.ForeignKey('account.User',
                              verbose_name=_('Owner'),
                              related_name='blacklist_owner', on_delete=models.CASCADE,)
    foe = models.ForeignKey('account.User',
                            verbose_name=_('Foe'),
                            related_name='blacked_user',
                            blank=True, null=True, default=None, on_delete=models.CASCADE)

    class Meta:
        """Meta-class"""
        verbose_name = _('Black list')
        verbose_name_plural = _('Black lists')


class UserLockQuerySet(models.QuerySet):
    """QuerySet for model UserLock"""
    pass


class UserLockManager(models.Manager):
    """Manager for model UserLock"""
    pass


class UserLock(BaseMixin):
    """Model for keep not valid login attempts."""

    user = models.OneToOneField('account.User', on_delete=models.CASCADE)
    # NOTE: это попытки входа или попытки ввода кода??
    attempts = models.PositiveSmallIntegerField(blank=True, null=True, default=0)
    attempt_timestamp = models.DateTimeField(blank=True, null=True, default=None,
                                             verbose_name=_('Last datetime authorization attempt'))
    objects = UserLockManager.from_queryset(UserLockQuerySet)()

    class Meta:
        """Meta class."""

        verbose_name = _('User lock')
        verbose_name_plural = _('User locks')

    def increment_attempts(self):
        """Increment attempts"""
        self.attempt_timestamp = timezone.now()
        self.attempts += 1
        self.save()

    def reset_attempts(self):
        """Reset attempts to verify sent sms code"""
        self.attempts = 0
        self.attempt_timestamp = None
        self.save()

    @property
    def datetime_before_unlock(self):
        """Datetime before for unlock"""
        last_attempt_datetime = self.modified
        timedelta_datetime = timezone.timedelta(seconds=settings.SMS_BLOCKING_PERIOD)
        return last_attempt_datetime + timedelta_datetime

    @property
    def remain_before_unlock(self):
        """Remaining time before unlock"""
        return (self.datetime_before_unlock - timezone.now()).seconds
