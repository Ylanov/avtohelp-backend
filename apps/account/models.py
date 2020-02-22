"""Account app models."""

import logging

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as AbstractUserManager
from django.contrib.gis.db.models.functions import Distance
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from base.models import PushNotificationConfiguration
from userprofile.models import Profile, ProfileGallery, ProfileLocation
from utils.mixins import BaseMixin
from userprofile.models import FCMDevice

# Logging error messages
logger = logging.getLogger('ACCOUNT')


class UserQuerySet(models.QuerySet):
    """Base User queryset"""

    def created(self):
        """Order by created date"""
        return self.order_by('-created')

    def by_phone(self, phone):
        """Queryset by user phone"""
        return self.filter(phone=phone)

    def annotate_geo_position_relevance(self):
        """Is the geo-position information current?"""
        geo_pos_settings = PushNotificationConfiguration.get_solo()
        return self.annotate(geo_position_is_valid=models.Case(
            #  Check if geo position is not Null
            models.When(profilelocation__location__isnull=False,
                        then=True),
            #  Check modified date
            models.When(profilelocation__modified__lte=(
                    timezone.now() - timezone.timedelta(hours=99)),
                then=True),
            models.When(profilelocation__modified__lte=(
                    timezone.now() - timezone.timedelta(minutes=0)),
                then=True),
            output_field=models.BooleanField(default=False),
            default=False
        ))

    def annotate_distance_from_assistance_request(self, assistance_request):
        """Annotate distance between user location and assistance request"""
        return self.annotate_geo_position_relevance().annotate(distance=models.Case(
            models.When(
                geo_position_is_valid=True,
                then=Distance('profilelocation__location', assistance_request.location))
        ))


class UserManager(AbstractUserManager):
    """Base User manager"""

    use_in_migrations = False

    def make(self, phone):
        """Default make-method for creating user"""

        obj = self.model(phone=phone)
        obj.save()
        #  Create profile obj for user
        Profile.objects.create(user=obj)
        #  Create profile location obj for user
        ProfileLocation.objects.create(user=obj)
        return obj

    def get_or_make(self, phone):
        """Get user object or make new one"""
        qs = User.objects.filter(phone=phone)
        if qs.exists():
            obj = (qs.first(), False)
            if not hasattr(obj[0], 'profile'):
                logger.info(f'INFO: {obj[0].phone} has no Profile obj.\n'
                            f'DATETIME: {timezone.now().isoformat()}.')
        else:
            obj = (self.make(phone=phone), True)
        return obj


class User(AbstractUser, BaseMixin):
    """Base user model."""

    phone = PhoneNumberField(
        verbose_name=_('Phone'), unique=True,
        error_messages={'unique': _("A user with that phone already exists.")},
    )
    username = models.CharField(_('username'), max_length=255, null=True,
                                blank=True, default=None)
    email = models.EmailField(_('email address'), blank=True,
                              null=True, default=None)
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ('username', 'email')

    objects = UserManager.from_queryset(UserQuerySet)()

    class Meta:
        """Meta class."""

        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        """String method."""
        return "%s:%s" % (self.phone, self.get_short_name())

    def logout(self):
        """Regenerate auth token method"""
        devices = FCMDevice.objects.filter(user_id=self.id).delete()
        self.auth_token.delete()
        logger.info(f'INFO: User ID:{self.id} has logout success.\n')

    @property
    def get_first_name(self):
        """Return user first_name"""
        return self.profile.first_name if hasattr(self, 'profile') else ''

    @property
    def get_last_name(self):
        """Return user last"""
        return self.profile.last_name if hasattr(self, 'profile') else ''

    @property
    def get_full_name(self):
        """Return user full name"""
        return f'{self.profile.first_name} {self.profile.last_name}' if hasattr(self, 'profile') else self.id

    @property
    def get_car_license_plate(self):
        """Return user profile car license plate"""
        return f'{self.profilecar_set.first().license_plate}' if self.profilecar_set.first() and  self.profilecar_set.first().license_plate else ''

    @property
    def get_avatar(self):
        """Return user profile avatar"""
        return self.profile.get_image_url()

    @property
    def get_location_update_datetime(self):
        """Return user location update datetime"""
        if self.profilelocation.location:
            return self.profilelocation.modified

    @property
    def location_is_valid(self):
        """Return boolean value if user update location is valid or not"""
        geo_pos_settings = PushNotificationConfiguration.get_solo()
        hours, minutes = geo_pos_settings.geo_position_lifetime.hour, geo_pos_settings.geo_position_lifetime.minute
        delta = timezone.now() - timezone.timedelta(hours=99, minutes=0)
        if self.get_location_update_datetime and self.get_location_update_datetime >= delta:
            return True
        else:
            return False

    @property
    def has_token(self):
        """Return boolean value if user has an auth token"""
        return True if hasattr(self, 'auth_token') else False
