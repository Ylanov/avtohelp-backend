from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from account.models import User
from authorization import models
from userprofile import models as profile_models
from utils import api_exceptions
from utils.methods import get_exception_body


class AuthorizationSerializer(serializers.ModelSerializer):
    """Serializer for model User"""

    phone = PhoneNumberField()

    class Meta:
        """Meta class"""

        model = models.User
        fields = ('id', 'phone')
        # NOTE: это что и за чем? создаем юзера когда захотим?

    def create(self, validated_data):
        """Override create method"""
        obj, created = User.objects.get_or_make(phone=validated_data.get('phone'))
        return obj


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

        # if it was sent last 30 seconds deny it.
        qs = models.SMSCode.objects.by_phone(phone)
        if qs.by_date().exists():
            unlock_time = qs.sent().order_by('created').last().created + timezone.timedelta(seconds=settings.SMS_SEND_DELAY)
            raise api_exceptions.TooOftenTriedError(detail={
                'detail': api_exceptions.TooOftenTriedError.default_detail,
                'remaining_time': (unlock_time - timezone.now()).seconds
            })

        # If user request sms-code more or equal then 3 times, raise TemporaryLockError
        # with remaining time in seconds
        sms_code_expired = qs.filter(
            created__lte=timezone.now() - timezone.timedelta(seconds=settings.SMS_BLOCKING_PERIOD))

        if qs.exists():
            # Set old sms-codes as expired if created date is old
            if sms_code_expired.exists(): sms_code_expired.update(status=models.SMSCode.EXPIRED)

            # If queryset filtered by status Sent and Waiting exists
            # write unlock date by this: last created sms-coded obj + SMS_BLOCKING_PERIOD
            if qs.ready_to_go():

                #NOTE: интересное условие, его аналог если я ничего не путаю if qs is not None
                unlock_time = qs.sent().order_by('created').last().created + timezone.timedelta(
                    seconds=settings.SMS_BLOCKING_PERIOD) if qs else None

                # Create remain time from unlock_time

                remain_time = (unlock_time - timezone.now()) if unlock_time else None

                # If exists sended sms-code and two declined, then raised exception
                if qs.sent().count() == 1 and qs.declined().count() == (settings.SMS_INPUT_ATTEMPTS - 1):
                    raise api_exceptions.TemporaryLockError(detail={
                        'detail': api_exceptions.TemporaryLockError.default_detail,
                        # NOTE: если предидущее условие сработает в else то remain_time будет равно None
                        # у которого нет свойства seconds, что приведет к ошибке
                        'remaining_time': remain_time.seconds
                    })

                # Else set status of previous sms-code to DECLINED
                else:
                    models.SMSCode.objects.decline_all_others(qs.sent().last())

                # NOTE: напиши эту логику на бумаге, есть подозрение что все много проще можно сделать
        return attrs

    def create(self, validated_data):
        """Create method."""
        # make a new sms
        obj = models.SMSCode.objects.make(**validated_data)
        # send actual sms logic
        obj.send_sms()
        return obj


class AuthenticationSerializer(serializers.ModelSerializer):
    """Authentication serializer"""

    # REQUEST
    code = serializers.CharField(label=_('Code'), required=True, write_only=True)
    phone = PhoneNumberField(label=_("Phone"), write_only=True)

    # RESPONSE
    token = serializers.CharField(read_only=True, source='user.auth_token')

    class Meta:
        """ Meta class """
        model = models.SMSCode
        fields = ('token', 'phone', 'code')

    def validate_code(self, value):
        """Validate code method."""

        def reset_attempts(obj):
            """Method for reset user attempts in UserLock model"""
            obj.attempts = 0
            obj.attempt_timestamp = None
            obj.save()
            # NOTE: итересный return
            # NOTE: to model
            return None

        # # Get user by his phone from init data
        user = User.objects.get(phone=self.initial_data.get('phone'))

        # Get or Create UserLock object by user
        user_lock = profile_models.UserLock.objects.get_or_create(user=user)[0]

        # Common checks
        # NOTE: через %time посмотри может эффективнее регулярку 0-9 длинной в SMS_CODE_LENGHT
        # само serializers.CharField запихать
        if not value.isdigit():
            raise serializers.ValidationError(_('Invalid code'))
        if len(value) != settings.SMS_CODE_LENGTH:
            raise serializers.ValidationError(_('Invalid code'))

        # Check user code
        qs = models.SMSCode.objects.by_phone(user.phone).by_code(value).sent()
        # if qs.exists():
        #     return qs.first()
        # else:
        #     profile_models.UserLock.objects.get_or_create(user=user)[0]
        #     raise Exception


        
        # 1000
        # 1001
        # 1002

        # 1003

        if not qs.exists():
            # Check for frequency for entering verification code, after first try
            if user_lock.attempts >= 1:

                # NOTE: вот тут не понял немного, подойдешь расскажешь при чем тут время задержки отправок смс
                             # 1.03.2019 10:00 - 1.03.2019 9:00 
                last_entry = timezone.now() - user_lock.attempt_timestamp
                    # 3600                   30
                if last_entry.seconds <= settings.SMS_SEND_DELAY:
                    raise api_exceptions.TooOftenTriedError(detail=get_exception_body(
                        api_exceptions.TooOftenTriedError))

            # If the code was entered settings.SMS_INPUT_ATTEMPTS times incorrectly,
            # then check lock time or reset attempts and decline all sended sms codes
            if user_lock.attempts == settings.SMS_INPUT_ATTEMPTS:
                unlock_time = user_lock.attempt_timestamp + timezone.timedelta(
                    seconds=settings.SMS_BLOCKING_PERIOD)

                # 1.03.2019 9:20 
                # 1.03.2019 9:30 
                # 1.03.2019 9:40 + 10
                
                # 1.03.2019 9:50  
                if unlock_time > timezone.now():
                    remain_time = unlock_time - timezone.now()
                    raise api_exceptions.TemporaryLockError({'detail': _('Temporary lock'),
                                                             'remaining_time': remain_time.seconds})
                else:
                    # Reset tryings
                    reset_attempts(user_lock)

                    # Decline all sended codes
                    models.SMSCode.objects.decline_all_by_user(user)
                    raise api_exceptions.TemporaryLockError(detail=get_exception_body(
                        api_exceptions.TemporaryLockError))
            # If attempts is in range from 0 to 3, then put timestamp and increase the counter
            else:
                user_lock.attempt_timestamp = timezone.now()
                user_lock.attempts += 1
                user_lock.save()
                # NOTE: to model
                raise api_exceptions.CodeIsNotAcceptedError(detail={
                    'remaining_attempts': settings.SMS_INPUT_ATTEMPTS - user_lock.attempts,
                    'status_code': api_exceptions.CodeIsNotAcceptedError.extended_status_code
                })
        # Reset tryings after enter correct code
        reset_attempts(user_lock)
        return qs.first()

    def create(self, validated_data):
        """Create or retrieve object"""

        smscode = validated_data.get('code')
        # find all other code records for this phone and make them DECLINED
        models.SMSCode.objects.decline_all_others(smscode)
        # and make a token
        token, created = Token.objects.get_or_create(user=smscode.user)
        # change status
        smscode.activate()
        smscode.save()
        # update the created time of the token to keep it valid

        if not created:
            token.created = timezone.now()
            # FIXIT: вот так делать не надо!!!
            # хочешь обновлять токен - дай ему поле modified/refreshed или вроде того
            # created - время когда номинально была сделана запись в таблице, не больше не меньше
            token.save()
        return smscode
