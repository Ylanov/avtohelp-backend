import logging

from celery import shared_task
from celery.schedules import crontab
from celery.task import periodic_task

from authorization import models as auth_models
from userprofile import models as profile_models
from order import models as order_models
from django.conf import settings
from django.utils import timezone


logger = logging.getLogger('CELERY')


@shared_task
def send_verification_sms(sms_code_id):
    """Send verification sms task."""
    # todo: add actual sending sms logic
    # Get sms code object
    sms = auth_models.SMSCode.objects.get(id=sms_code_id)

    if settings.USE_SMS is True:
        # send actual sms if its allowed by server configuration
        try:
            sms.send()
            logger.info('SMS: sending try, ID=%d' % sms.id)
        except:
            logger.error('SMS: sending failed, ID=%d' % sms.id)
    else:
        # or fake it
        sms.fake()
        logger.info('SMS: debug sending, ID=%d' % sms.id)


@shared_task
def not_completed_authorization(user_id):
    """Authorization was not completed"""

    try:
        reset_attempts(user_id=user_id)
        auth_models.SMSCode.objects.decline_all_by_user(user=user_id)
    except:
        logger.info(f'ERROR: authorization was not completed for user {user_id}')


@shared_task
def success_authorization(user_id):
    """Finish of success authorization"""
    try:
        reset_attempts(user_id=user_id)
        change_smscode_status(user_id=user_id, status=auth_models.SMSCode.ACTIVATED)
        auth_models.SMSCode.objects.decline_all_by_user(user=user_id)
    except:
        logger.info(f'ERROR: success authorization was not completed for user {user_id}')


@shared_task
def reset_attempts(user_id):
    """Reset user attempts"""

    userlock_qs = auth_models.UserLock.objects.filter(user=user_id)
    # reset attempts
    if userlock_qs.exists():
        userlock_qs.first().reset_attempts()


@shared_task
def change_smscode_status(user_id, status):
    """Change SMSCode object status"""

    smscode = auth_models.SMSCode.objects.get(user=user_id)
    smscode.status = status
    smscode.save()


@periodic_task(run_every=crontab(minute=settings.REQUEST_RELEVANCE))
def check_request_relevance():
    """Check relevance of assistance requests"""
    timedelta = timezone.now() + timezone.timedelta(minutes=settings.REQUEST_RELEVANCE)
    available_requests = order_models.AssistanceRequest.objects.by_status(
        status=order_models.AssistanceRequest.AVAILABLE)
    if available_requests.exists():
        for request in available_requests:
            expired_date = request.created + timezone.timedelta(minutes=settings.REQUEST_RELEVANCE)
            if expired_date >= timedelta:
                request.status = order_models.AssistanceRequest.EXPIRED
                request.save()
