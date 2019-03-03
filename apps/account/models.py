"""Account app models."""

from django.contrib.auth.models import AbstractUser, UserManager as AbstractUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from userprofile.models import Profile, FriendList, BlackList
from utils.mixins import BaseMixin

"""
MANAGERS
"""


class UserManager(AbstractUserManager):
    """Base User manager"""

    use_in_migrations = False

    def make(self, phone):
        """Default make-method for creating user"""

        obj = self.model(phone=phone)
        obj.save()

        Profile.objects.create(user=obj)
        BlackList.objects.create(owner=obj)
        FriendList.objects.create(owner=obj)
        return obj

    def get_or_make(self, phone):
        """Get user object or make new one"""
        qs = User.objects.filter(phone=phone)
        if qs.exists():
            obj = qs.first(), False
        else:
            obj = self.make(phone=phone), True
        return obj


"""
QUERYSETS
"""


class UserQuerySet(models.QuerySet):
    """Base User queryset"""

    def created(self):
        """Order by created date"""
        return self.order_by('-created')

    def by_phone(self, phone):
        """Queryset by user phone"""
        return self.filter(phone=phone)


"""
MODELS
"""


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
        self.auth_token.delete()

    def get_first_name(self):
        """Return user first_name"""
        return self.profile.first_name if self.profile else None

    def get_last_name(self):
        """Return user last"""
        return self.profile.last_name if self.profile else None

    def get_middle_name(self):
        """Return user middle_name"""
        return self.profile.middle_name if self.profile else None
