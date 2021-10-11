from datetime import timedelta
from datetime import datetime
import calendar, time
import hashlib

import requests
import json
import logging
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from account.models import User
from utils.methods import generate_sms_code
from utils.mixins import BaseMixin

# Logging error messages
logger = logging.getLogger("CELERY")

# Create your models here.
class SMSCodeManager(models.Manager):
    """Extended manager for SMSCode model."""

    def make(self, phone, mode=0, status=None, user=None, code=None):
        """Make new sms code object."""
        obj = self.model(phone=phone)
        obj.user = user or User.objects.by_phone(phone).first()
        obj.code = code or generate_sms_code()
        obj.mode = mode
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
        if isinstance(user, int):
            user = User.objects.get(id=user)
        # find all other code records for this phone
        qs = self.by_phone(user.phone).ready_to_go()
        # make them DECLINED
        qs.update(status=self.model.DECLINED)

    def decline_all_by_phone(self, phone):
        """Set status declined on all records."""
        user = User.objects.get(phone=phone)
        # find all other code records for this phone
        qs = self.by_phone(user.phone).ready_to_go()
        # make them DECLINED
        qs.update(status=self.model.DECLINED)


class SMSCodeQuerySet(models.query.QuerySet):
    """Extended queryset for SMSCode model."""

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

    def expired(self, minutes=settings.SMS_BLOCKING_PERIOD):
        """Filter expired codes."""
        delta = timezone.now() - timedelta(minutes=minutes)
        return self.filter(created__lte=delta).ready_to_go()

    def ordered(self):
        """Default ordering."""
        return self.order_by("-id")

    def ready_to_go(self):
        """Filter only waiting and sent codes."""
        return self.filter(status__in=[self.model.SENT, self.model.WAITING])

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

    URL = "http://smsc.ru/sys/send.php"
    LOGIN = settings.SMS_LOGIN
    PASSWORD = settings.SMS_PASSWORD

    WAITING = 0
    SENT = 1
    ACTIVATED = 2
    DECLINED = 3
    EXPIRED = 4

    SMS = 0
    CALL = 1

    STATUS_CHOICES = (
        (WAITING, _("Waiting")),
        (SENT, _("Sent")),
        (ACTIVATED, _("Activated")),
        (DECLINED, _("Declined")),
        (EXPIRED, _("Expired")),
    )

    MODE_CHOICES = ((SMS, "SMS"), (CALL, "CALL"))

    phone = PhoneNumberField(verbose_name=_("Phone"))
    user = models.ForeignKey(
        "account.User",
        default=None,
        null=True,
        blank=True,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
    )

    mode = models.PositiveSmallIntegerField(default=SMS, choices=MODE_CHOICES)
    status = models.PositiveSmallIntegerField(default=WAITING, choices=STATUS_CHOICES)
    code = models.CharField(max_length=settings.SMS_CODE_LENGTH, verbose_name=_("Code"))

    objects = SMSCodeManager.from_queryset(SMSCodeQuerySet)()

    class Meta:
        """Meta class."""

        verbose_name = _("SMS code")
        verbose_name_plural = _("SMS codes")

    def __str__(self):
        """String method."""
        return self.phone.as_e164 if hasattr(self.phone, "as_e164") else "SMS"

    def generate_code(self):
        """Code generation method."""
        self.code = generate_sms_code()

    def send_sms(self):
        """Send sms method."""
        message = _("Verification code is %s.\nRoad.Helper") % self.code
        params = {
            "login": settings.SMS_LOGIN,
            "psw": settings.SMS_PASSWORD,
            # 'sender': settings.SMS_SENDER,
            "phones": self.phone.as_e164,
            "mes": message,
        }
        requests.post(url=self.URL, params=params)
        self.status = self.SENT
        self.save()

    def phone_call(self):
        """Phone call method."""
        endpoint = "call/start-password-call"
        logger.info("endpoint: " + endpoint)
        url = settings.OTP_SERVICE + "/" + endpoint
        server_key = settings.OTP_SERVER_KEY
        server_signature_key = settings.OTP_SIGNATURE_KEY

        data = {
            "async": 1,
            "dstNumber": self.phone.as_e164.replace("+", ""),
            "pin": self.code,
            "timeout": 20,
        }
        data = json.dumps(data)
        logger.info("data: " + data)

        timestamp = str(calendar.timegm(time.gmtime()))
        logger.info("timestamp: " + timestamp)

        signature_text = "%s\n%s\n%s\n%s\n%s" % (
            endpoint,
            timestamp,
            server_key,
            data,
            server_signature_key,
        )

        sha_signature = hashlib.sha256(signature_text.encode()).hexdigest()
        logger.info("sha_signature: " + sha_signature)
        access_token = server_key + timestamp + sha_signature
        logger.info("access_token: " + access_token)

        headers = {
            "Content-type": "application/json",  # Определение типа данных
            "Authorization": "Bearer " + access_token,
        }

        response = requests.post(url=url, headers=headers, data=data)
        logger.info("response: " + response.text)

        self.status = self.SENT
        self.save()

    def fake(self):
        """Fake send sms method"""
        self.status = self.SENT
        self.save()

    def activate(self):
        """Activate code."""
        self.status = self.ACTIVATED
        self.save()

    @property
    def datetime_before_resend(self):
        """Datetime before for re-request sms code"""
        last_sms_datetime = SMSCode.objects.order_by("created").last().created
        timedelta_datetime = timezone.timedelta(seconds=settings.SMS_SEND_DELAY)
        return last_sms_datetime + timedelta_datetime

    @property
    def datetime_before_unlock(self):
        """Datetime before for unlock"""
        last_sms_datetime = SMSCode.objects.order_by("created").last().created
        timedelta_datetime = timezone.timedelta(seconds=settings.SMS_BLOCKING_PERIOD)
        return last_sms_datetime + timedelta_datetime

    @property
    def remain_before_resend(self):
        """Remaining time before re-request sms code"""
        return (self.datetime_before_resend - timezone.now()).seconds

    @property
    def remain_before_unlock(self):
        """Remaining time before unlock"""
        return (self.datetime_before_unlock - timezone.now()).seconds


class UserLockQuerySet(models.QuerySet):
    """QuerySet for model UserLock"""

    def by_phone(self, phone):
        """Filter user lock by phone number"""
        return self.filter(user__phone=phone)


class UserLockManager(models.Manager):
    """Manager for model UserLock"""

    pass


class UserLock(BaseMixin):
    """Model for keep not valid login attempts."""

    user = models.OneToOneField("account.User", on_delete=models.CASCADE)
    attempts = models.PositiveSmallIntegerField(blank=True, null=True, default=0)
    attempt_timestamp = models.DateTimeField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Last datetime authorization attempt"),
    )
    objects = UserLockManager.from_queryset(UserLockQuerySet)()

    class Meta:
        """Meta class."""

        verbose_name = _("User lock")
        verbose_name_plural = _("User locks")

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
