from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from account.models import User
from authorization import models
from userprofile import models as profile_models
from utils import api_exceptions, tasks
from utils.mixins import AuthorizationMixin


class PhoneVerificationSerializer(serializers.ModelSerializer):
    """Verification phone serializer"""

    phone = PhoneNumberField(write_only=True)

    class Meta:
        """Override create method"""

        model = models.SMSCode
        fields = ('phone',)

    def validate(self, attrs):
        """Validate method."""
        phone = attrs.get('phone')
        # get sms-codes by user phone
        qs = models.SMSCode.objects.by_phone(phone)
        if qs.exists():
            # if it was sent last 30 seconds deny it.
            if qs.by_date().exists():
                raise api_exceptions.TooOftenTriedError(detail={
                    'detail': api_exceptions.TooOftenTriedError.default_detail,
                    'remaining_time': self.Meta.model().remain_before_resend
                })
            elif qs.count() >= 3:
                raise api_exceptions.TemporaryLockError(detail={
                    'detail': api_exceptions.TooOftenTriedError.default_detail,
                    'remaining_time': f'{self.Meta.model().remain_before_resend}'
                })
        return attrs

    def create(self, validated_data):
        """Create method."""
        # make a new sms
        obj = models.SMSCode.objects.make(user=User.objects.get_or_make(phone=validated_data.get('phone'))[0],
                                          **validated_data)
        # send actual sms logic
        obj.send_sms()
        return obj


class AuthorizationView(serializers.ModelSerializer, AuthorizationMixin):
    """Authentication serializer"""

    # REQUEST
    code = serializers.IntegerField(label=_('Code'), required=True, write_only=True)
    phone = PhoneNumberField(label=_("Phone"), write_only=True)

    # RESPONSE
    token = serializers.CharField(read_only=True, source='user.auth_token')

    class Meta:
        """ Meta class """
        model = models.SMSCode
        fields = ('token', 'phone', 'code')

    def validate(self, attrs):
        """Validation method"""
        user = User.objects.get(phone=attrs.get('phone'))

        # check user code
        qs = models.SMSCode.objects.by_phone(user.phone).by_code(attrs.get('value')).sent()

        # if code is correct return SMSCode object
        if qs.exists():
            if settings.USE_CELERY:
                tasks.reset_user_attempts.delay(user_id=user.id)
            else:
                tasks.reset_user_attempts(user_id=user.id)
            return qs.first()
        else:
            # get or create UserLock object by user
            user_lock = profile_models.UserLock.objects.get_or_create(user=user)[0]

            # check if attempts exhausted
            if user_lock.attempts == settings.SMS_INPUT_ATTEMPTS:
                # check is it possible to try again
                if user_lock.datetime_before_unlock > timezone.now():
                    raise api_exceptions.TemporaryLockError(detail={
                        'detail': api_exceptions.TemporaryLockError.default_detail,
                        'remaining_time': user_lock.remain_before_unlock
                    })
                else:
                    if settings.USE_CELERY:
                        tasks.reset_user_attempts.delay(user_id=user.id)
                    else:
                        tasks.reset_user_attempts(user_id=user.id)
                    raise api_exceptions.TemporaryLockError(detail={
                        'detail': api_exceptions.TemporaryLockError.default_detail,
                        'remaining_time': user_lock.remain_before_unlock
                    })
            # regular behavior
            else:
                user_lock.increment_attempts()
                raise api_exceptions.CodeIsNotAcceptedError(detail={
                    'remaining_attempts': settings.SMS_INPUT_ATTEMPTS - user_lock.attempts,
                    'status_code': api_exceptions.CodeIsNotAcceptedError.extended_status_code
                })

    def create(self, validated_data):
        """Create or retrieve object"""
        smscode = validated_data.get('code')
        # find all other code records for this phone and make them DECLINED
        models.SMSCode.objects.decline_all_others(smscode)
        # and make a token
        Token.objects.get_or_create(user=smscode.user)
        # change status
        smscode.activate()
        return smscode
