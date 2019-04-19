import logging

from celery import shared_task
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from fcm_django.models import FCMDevice
from django.utils.timezone import timedelta

from account import models as account_models
from authorization import models as auth_models
from base import models as base_models
from online_users.models import OnlineUserActivity

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
        auth_models.SMSCode.objects.decline_all_by_user(user_id=user_id)
    except:
        logger.info(f'ERROR: authorization was not completed for user {user_id}')


@shared_task
def success_authorization(user_id, sms_code_id):
    """Finish of success authorization"""
    try:
        reset_attempts(user_id=user_id)
        change_smscode_status(sms_code_id=sms_code_id, status=auth_models.SMSCode.ACTIVATED)
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
def change_smscode_status(sms_code_id, status):
    """Change SMSCode object status"""
    smscode = auth_models.SMSCode.objects.get(id=sms_code_id)
    smscode.status = status
    smscode.save()


# Conflict with daphne
# @periodic_task(run_every=crontab(minute=settings.REQUEST_RELEVANCE))
# def check_request_relevance():
#     """Check relevance of assistance requests"""
#     available_requests = order_models.AssistanceRequest.objects.exclude(
#         status=order_models.AssistanceRequest.EXPIRED)
#     if available_requests.exists():
#         for request in available_requests:
#             expired_date = request.created + timezone.timedelta(minutes=settings.REQUEST_RELEVANCE)
#             if timezone.now() >= expired_date:
#                 request.status = order_models.AssistanceRequest.EXPIRED
#                 request.save()


@shared_task
def notify_friend_request(invited_id):
    """Notify user about new friend request"""
    notification = base_models.PushNotification.objects.create(
        user_id=invited_id,
        title=_('New friend request'),
        description=_('A new friend request has been received')
    )
    devices = FCMDevice.objects.filter(user_id=invited_id)
    if devices.exists():
        count = devices.send_message(**notification.get_push_dict())
        if count > 0:
            logger.info(f'Users notified: {count.get("success")}')
        else:
            logger.info(f'Error was occurred when sending PUSH-notifications')


@shared_task
def notify_chat_participants(sender_id, participants):
    """Notify user about new friend request"""
    sender = account_models.User.objects.get(id=sender_id)
    for user_id in participants:
        # Check if user is online
        notification = base_models.PushNotification.objects.create(
            user_id=user_id,
            title=_('New message from chat'),
            description=_(f'User {sender.get_full_name()} wrote a message')
        )
        devices = FCMDevice.objects.filter(user_id=user_id)
        if devices.exists():
            count = devices.send_message(**notification.get_push_dict())[0]
            if count.get('success') > 0:
                notification.status = True
                notification.save()
                logger.info(f'Users notified: {count.get("success")}')
            else:
                logger.info(f'Error was occurred when sending PUSH-notifications. Failed: {count.get("failure")}')


@shared_task
def notify_users():
    """Notify users about assistance request"""
    devices = FCMDevice.objects.all()
    for device in devices:
        notification = base_models.PushNotification.objects.create(
            user=device.user,
            title=_('New assistance request'),
            description=_('New assistance request was published')
        )
        count = devices.send_message(**notification.get_push_dict())
        if count.get('success') > 0:
            notification.status = True
            notification.save()
            logger.info(f'Users notified: {count.get("success")}')
        else:
            logger.info(f'Error was occurred when sending PUSH-notifications. Failed: {count.get("failure")}')


# Conflict with daphne
# @periodic_task(run_every=crontab(minute=settings.MESSAGES_UPDATE_PERIOD))
# def notify_unread_messages(title, body):
#     """Notify users about unread messages"""
#     rooms = chat_models.ChatRoom.objects.all()
#     for room in rooms:
#         notify = list()
#         for participant in room.participants.all():
#             message_count = room.chatmessage_set.exclude(sender=participant).count()
#             read_messages = chat_models.ChatReadMessage.objects.filter(user=participant).count()
#             if (message_count - read_messages) > settings.LIMIT_UNREAD_MESSAGES:
#                 notify.append(participant)
#             # for message in room.chatmessage_set.all():
#             #     qs = chat_models.ChatReadMessage.objects.filter(message=message, user=participant)
#             #     if not qs.exists():
#             #         notify.append(participant)
#         if notify:
#             for user in notify:
#                 notification = base_models.PushNotification.objects.create(
#                     user=user,
#                     title=_('Unread messages'),
#                     description=_('You have unread messages')
#                 )
#                 devices = FCMDevice.objects.filter(user=user)
#                 if devices.exists():
#                     count = devices.send_message(**notification.get_push_dict())
#                     if count.get('success') > 0:
#                         notification.status = True
#                         notification.save()
#                         logger.info(f'Users notified: {count.get("success")}')
#                     else:
#                         logger.info(
#                             f'Error was occurred when sending PUSH-notifications. Failed: {count.get("failure")}')
#         notify.clear()
