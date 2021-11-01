import logging

from django.conf import settings
from django.utils import timezone

from authorization.models import (
    SMSCode,
    UserLock,
)
from roadhelpbackend.celery import app

logger = logging.getLogger("CELERY")


@app.task
def not_completed_authorization(user_id):
    """Authorization was not completed"""

    try:
        reset_attempts(user_id=user_id)
        SMSCode.objects.decline_all_by_user(user_id=user_id)
    except (Exception,):
        logger.info(
            f"ERROR: authorization was not completed for user {user_id}"
        )


@app.task
def change_smscode_status(sms_code_id, status):
    """Change SMSCode object status"""

    smscode = SMSCode.objects.get(id=sms_code_id)
    smscode.status = status
    smscode.save()


@app.task
def check_verification_sms_relevance():
    """Check verification SMS relevance"""

    for sms_code in SMSCode.objects.filter(status=SMSCode.SENT):
        delta = sms_code.created + timezone.timedelta(
            seconds=settings.SMS_BLOCKING_PERIOD
        )
        if timezone.now() <= delta:
            sms_code.status = SMSCode.EXPIRED
            sms_code.save()


@app.task
def send_verification_sms(sms_code_id):
    """Send verification sms task."""

    # Get sms code object
    sms = SMSCode.objects.get(id=sms_code_id)

    if settings.USE_SMS is True and sms.user.phone != settings.APPROVE_ACCOUNT:
        # send actual sms if its allowed by server configuration
        try:
            logger.info("DEBUG: sms.mode=%s" % sms.mode)

            # check verification mode is CALL PHONE
            if sms.mode == 1:
                # call
                sms.phone_call()
                logger.info("SMS: phone call try, ID=%d" % sms.id)
            else:
                # send sms
                sms.send_sms()
                logger.info("SMS: sending try, ID=%d" % sms.id)
        except (Exception,):
            logger.error("SMS: sending failed, ID=%d" % sms.id)
    else:
        # or fake it
        sms.fake()
        logger.info("SMS: debug sending, ID=%d" % sms.id)


@app.task
def reset_attempts(user_id):
    """Reset user attempts"""
    userlock_qs = UserLock.objects.filter(user=user_id)
    # reset attempts
    if userlock_qs.exists():
        userlock_qs.first().reset_attempts()


@app.task
def success_authorization(user_id, sms_code_id):
    """Finish of success authorization"""
    try:
        reset_attempts(user_id=user_id)
        change_smscode_status(
            sms_code_id=sms_code_id,
            status=SMSCode.ACTIVATED,
        )
        SMSCode.objects.decline_all_by_user(user=user_id)
    except (Exception,):
        logger.info(
            f"ERROR: success authorization was not completed for user {user_id}"  # noqa
        )
