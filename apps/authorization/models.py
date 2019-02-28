import logging
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from account.models import User
from utils.methods import generate_sms_code
from utils.mixins import BaseMixin
from utils.tasks import send_verification_sms

logger = logging.getLogger('AUTHORIZATION')


# Create your models here.
class SMSCodeManager(models.Manager):
    """Extended manager for SMSCode model."""

    def make(self, phone, status=None, user=None, code=None):
        """Make new sms code object."""
        obj = self.model(phone=phone)
        obj.user = user or User.objects.by_phone(phone).first()
        obj.code = code or generate_sms_code()
        if status:
            obj.status = status
        obj.save()
        return obj

    def decline_all_others(self, obj):
        """Set status declined on all records, except that."""
        # Considering phone of course.
        # find all other code records for this phone
        qs = self.by_phone(obj.phone).ready_to_go()
        # make them DECLINED
        qs.update(status=self.model.DECLINED, user=obj.user)

    def decline_all_by_user(self, user):
        """Set status declined on all records."""
        # find all other code records for this phone
        qs = self.by_phone(user.phone).ready_to_go()
        # make them DECLINED
        qs.update(status=self.model.DECLINED)


class SMSCodeQuerySet(models.query.QuerySet):
    """Extended querysets for SMSCode model."""

    def by_phone(self, phone):
        """Phone filter."""
        return self.filter(phone=phone)

    def by_user(self, user=None):
        """User filter."""
        if user:
            return self.filter(user=user)
        else:
            return self.filter(user__isnunll=True)

    def by_code(self, code):
        """Code filter."""
        return self.filter(code=code)

    def by_date(self, seconds=settings.SMS_SEND_DELAY):
        """Filter by date."""
        delta = timezone.now() - timedelta(seconds=seconds)
        return self.filter(modified__gte=delta)

    def expired(self, minutes=settings.SMS_EXPIRATION):
        """Filter expirder codes."""
        delta = timezone.now() - timedelta(minutes=minutes)
        return self.filter(created__lte=delta).ready_to_go()

    def ordered(self):
        """Default ordering."""
        return self.order_by('-id')

    def ready_to_go(self):
        """Filter only waiting and sent codes."""
        return self.filter(status__in=[self.model.SENT,
                                       self.model.WAITING])

    def declined(self):
        """Filter only declined codes."""
        return self.filter(status=self.model.DECLINED)

    def sent(self):
        """Filter only sent codes."""
        return self.filter(status=self.model.SENT)

    def get_sent_code(self, user):
        """Return queryset SMSCode filter by user and SENT-status"""
        return self.by_user(user).sent()


class SMSCode(BaseMixin):
    """Sms codes model."""

    WAITING = 0
    SENT = 1
    ACTIVATED = 2
    DECLINED = 3
    EXPIRED = 4

    STATUS_CHOICES = (
        (WAITING, _('Waiting')),
        (SENT, _('Sent')),
        (ACTIVATED, _('Activated')),
        (DECLINED, _('Declined')),
        (EXPIRED, _('Expired'))
    )

    phone = PhoneNumberField(verbose_name=_('Phone'))
    user = models.ForeignKey('account.User', default=None,
                             null=True, blank=True, verbose_name=_('User'),
                             on_delete=models.CASCADE)

    status = models.PositiveSmallIntegerField(
        default=WAITING, choices=STATUS_CHOICES)
    code = models.CharField(max_length=settings.SMS_CODE_LENGTH, verbose_name=_('Code'))

    objects = SMSCodeManager.from_queryset(SMSCodeQuerySet)()

    class Meta:
        """Meta class."""

        verbose_name = _('SMS code')
        verbose_name_plural = _('SMS codes')

    def __str__(self):
        """String method."""
        return self.phone.as_e164 if hasattr(self.phone, 'as_e164') else 'SMS'

    def generate_code(self):
        """Code generation method."""
        self.code = generate_sms_code()

    def send_sms(self):
        """Send sms method."""
        self.status = self.SENT
        self.save()
        # put sms sending task in queue
        # used as simple method due to celery issues
        if settings.USE_CELERY:
            send_verification_sms.delay(sms_code_id=self.id)
        else:
            logger.debug('Send SMS')

    def activate(self):
        """Activate code."""
        self.status = self.ACTIVATED
