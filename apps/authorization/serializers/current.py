from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from account.models import User
from authorization import models
from catalog import models as catalog_models
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
                    'remaining_time': qs.first().remain_before_resend
                })
            elif qs.count() >= 3:
                raise api_exceptions.TemporaryLockError(detail={
                    'detail': api_exceptions.TooOftenTriedError.default_detail,
                    'remaining_time': qs.first().remain_before_resend
                })
        return attrs

    def create(self, validated_data):
        """Create method."""
        # make a new user
        user = User.objects.get_or_make(phone=validated_data.get('phone'))[0]
        # make a new sms
        obj = models.SMSCode.objects.make(user=user,  **validated_data)
        # send actual sms logic
        if settings.USE_CELERY:
            tasks.send_verification_sms.delay(sms_code_id=obj.id)
        else:
            tasks.send_verification_sms(sms_code_id=obj.id)
        return obj


class ProfileMinSerializer(serializers.ModelSerializer):
    """Minimized profile information"""

    class Meta:
        """Meta class"""
        model = profile_models.Profile
        fields = ('id', 'created', 'first_name', 'last_name',
                  'middle_name')


class AuthorizationView(serializers.ModelSerializer):
    """Authentication serializer"""

    # REQUEST
    code = serializers.CharField(write_only=True)
    phone = PhoneNumberField(write_only=True)

    # RESPONSE
    token = serializers.CharField(read_only=True, source='user.auth_token')
    profile = ProfileMinSerializer(read_only=True, source='user.profile')

    class Meta:
        """ Meta class """
        model = models.SMSCode
        fields = ('token', 'phone', 'code', 'profile')

    def validate(self, attrs):
        """Validation method"""
        user = User.objects.get(phone=attrs.get('phone'))

        # check user code
        qs = models.SMSCode.objects.by_phone(user.phone).by_code(attrs.get('code')).sent()

        # if code is correct return SMSCode object
        if qs.exists():
            # put SMSCode object instead of code number
            attrs['code'] = qs.first()
            if settings.USE_CELERY:
                tasks.success_authorization.delay(user_id=user.id)
            else:
                tasks.success_authorization(user_id=user.id)
            return attrs
        else:
            # get or create UserLock object by user
            user_lock = models.UserLock.objects.get_or_create(user=user)[0]

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
                        tasks.not_completed_authorization.delay(user_id=user.id)
                    else:
                        tasks.not_completed_authorization(user_id=user.id)
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
        smscode = validated_data['code']
        # make a token
        Token.objects.get_or_create(user=smscode.user)
        return smscode
