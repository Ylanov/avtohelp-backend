import logging

from celery import shared_task

from authorization import models as authorization_models

logger = logging.getLogger('CELERY')


@shared_task
def send_verification_sms(phone, sms_code_id):
    """Send verification sms task."""
    # todo: add actual sending sms logic
    # Get sms code object
    code_object = authorization_models.SMSCode.objects.get(id=sms_code_id)
    # Add logic to change flag to activated after succeeded sent
