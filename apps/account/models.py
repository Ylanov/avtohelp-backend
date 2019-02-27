"""Account app models."""

from django.contrib.auth.models import AbstractUser, UserManager as AbstractUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _
from userprofile.models import Profile, FriendList, BlackList

from phonenumber_field.modelfields import PhoneNumberField


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


"""
QUERYSETS
"""


class UserQuerySet(models.QuerySet):
    """Base User queryset"""

    def created(self):
        return self.order_by('-created')


"""
MODELS
"""


class User(AbstractUser):
    """Base user model."""

    phone = PhoneNumberField(
        verbose_name=_('Phone'), unique=True,
        error_messages={'unique': _("A user with that phone already exists.")},
    )
    username = models.CharField(_('username'), max_length=255, null=True,
                                blank=True, default=None)
    email = models.EmailField(_('email address'), blank=True,
                              null=True, default=None)
    patronymic = models.CharField(_('patronymic'), max_length=30, blank=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username', 'email']

    objects = UserManager.from_queryset(UserQuerySet)()

    class Meta:
        """Meta class."""

        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        """String method."""
        return "%s:%s" % (self.phone.as_e164, self.get_short_name())
