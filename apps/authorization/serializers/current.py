# todo: delete after testing
from os import environ

from django.conf import settings
from django.utils import timezone
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from account.models import User
from authorization import models
from project import celery as tasks
from userprofile import models as profile_models
from utils import api_exceptions


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
        user_qs = User.objects.filter(phone=phone)
        # check if user phone is active or not
        if user_qs.exists() and not user_qs.first().is_active:
            raise api_exceptions.UserIsBlocked()

        # no check is debug
        if settings.DEBUG:
            return attrs

        # get sms-codes by user phone
        qs = models.SMSCode.objects.by_phone(phone).ready_to_go()
        if qs.exists():
            # if it was sent last 30 seconds deny it.
            if qs.by_date().exists() and qs.count() < 3:
                raise api_exceptions.TooOftenTriedError(detail={
                    'detail': api_exceptions.TooOftenTriedError.default_detail,
                    'remaining_time': qs.first().remain_before_resend
                })
            elif qs.count() >= 3:
                if not timezone.now() > qs.first().datetime_before_unlock:
                    raise api_exceptions.TemporaryLockError(
                        remaining_time=qs.first().remain_before_unlock)
                else:
                    models.SMSCode.objects.decline_all_by_phone(phone=phone)
        return attrs

    def create(self, validated_data):
        """Create method."""
        # make a new user
        user = User.objects.get_or_make(phone=validated_data.get('phone'))[0]
        # make a new sms
        # todo: remove from prod, this was added temporarily
        if environ.get('SETTINGS_CONFIGURATION') in ('local', 'development') or\
           validated_data.get('phone') == '+79180055555':
            obj = models.SMSCode.objects.make(user=user, code=12345, **validated_data)
        else:
            obj = models.SMSCode.objects.make(user=user, **validated_data)
        if settings.USE_CELERY:
            tasks.send_verification_sms.delay(sms_code_id=obj.id)
        else:
            tasks.send_verification_sms(sms_code_id=obj.id)
        return obj

    def to_representation(self, instance):
        """Override to_representation method"""
        import os
        configuration = os.environ.get('SETTINGS_CONFIGURATION')
        if (configuration == 'local') or (configuration == 'development'):
            return {'code': instance.code}
        return super(PhoneVerificationSerializer, self).to_representation(instance)


class ProfileMinSerializer(serializers.ModelSerializer):
    """Minimized profile information"""

    class Meta:
        """Meta class"""
        model = profile_models.Profile
        fields = ('id', 'created', 'first_name', 'last_name')


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
        user_qs = User.objects.filter(phone=attrs.get('phone'))
        if not user_qs.exists():
            raise api_exceptions.UserNotFound()
        else:
            user = user_qs.first()

        # check user code
        qs = models.SMSCode.objects.by_phone(user.phone).by_code(attrs.get('code')).sent()

        # if code is correct return SMSCode object
        if qs.exists():
            # put SMSCode object instead of code number
            attrs['code'] = qs.first()
            if settings.USE_CELERY:
                tasks.success_authorization.delay(user_id=user.id, sms_code_id=attrs['code'].id)
            else:
                tasks.success_authorization(user_id=user.id, sms_code_id=attrs['code'].id)
            return attrs
        else:
            # get or create UserLock object by user
            user_lock = models.UserLock.objects.get_or_create(user=user)[0]

            # check if attempts exhausted
            if user_lock.attempts == settings.SMS_INPUT_ATTEMPTS:
                # check is it possible to try again
                if user_lock.datetime_before_unlock > timezone.now():
                    raise api_exceptions.TemporaryLockError(
                        remaining_time=user_lock.remain_before_unlock)
                else:
                    if settings.USE_CELERY:
                        tasks.not_completed_authorization.delay(user_id=user.id)
                    else:
                        tasks.not_completed_authorization(user_id=user.id)
                    raise api_exceptions.TemporaryLockError(
                        remaining_time=user_lock.remain_before_unlock)
            # regular behavior
            else:
                user_lock.increment_attempts()
                raise api_exceptions.CodeIsNotAcceptedError(
                    remaining_attempts=settings.SMS_INPUT_ATTEMPTS - user_lock.attempts,
                    status_code=api_exceptions.CodeIsNotAcceptedError.extended_status_code)

    def create(self, validated_data):
        """Create or retrieve object"""
        smscode = validated_data['code']
        # make a token
        Token.objects.get_or_create(user=smscode.user)
        return smscode
