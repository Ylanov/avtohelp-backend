import logging

from celery import shared_task

from authorization import models as auth_models
from userprofile import models as profile_models
from account import models as account_models


logger = logging.getLogger('CELERY')


@shared_task
def send_verification_sms(phone, sms_code_id):
    """Send verification sms task."""
    # todo: add actual sending sms logic
    # Get sms code object
    code_object = auth_models.SMSCode.objects.get(id=sms_code_id)
    # Add logic to change flag to activated after succeeded sent


@shared_task
def reset_user_attempts(user_id):
    """Reset user attempts"""
    user = account_models.User.objects.get(id=user_id)
    user_lock = profile_models.UserLock.objects.get(user=user_id)

    # reset attempts
    user_lock.reset_attempts()

    # decline all sent codes
    auth_models.SMSCode.objects.decline_all_by_user(user)
