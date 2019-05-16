import logging
import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Logging error messages
logger = logging.getLogger('CELERY')


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls check_request_relevance() every 30 minutes.
    sender.add_periodic_task(crontab(minute=settings.REQUEST_RELEVANCE),
                             check_request_relevance.s(),
                             name='Check assistance request relevance')
    # Unused
    # sender.add_periodic_task(crontab(minute=settings.MESSAGES_UPDATE_PERIOD),
    #                          notify_unread_messages.s(),
    #                          name='Notify users about unread messages')


@app.task
def check_request_relevance():
    """Check relevance of assistance requests"""
    from order import models as order_models
    available_requests = order_models.AssistanceRequest.objects.exclude(
        status=order_models.AssistanceRequest.EXPIRED)
    if available_requests.exists():
        for request in available_requests:
            expired_date = request.created + timezone.timedelta(minutes=settings.REQUEST_RELEVANCE)
            if timezone.now() >= expired_date:
                request.status = order_models.AssistanceRequest.EXPIRED
                request.save()


@app.task
def send_verification_sms(sms_code_id):
    """Send verification sms task."""
    from authorization import models as auth_models
    # Get sms code object
    sms = auth_models.SMSCode.objects.get(id=sms_code_id)

    if settings.USE_SMS is True:
        # send actual sms if its allowed by server configuration
        try:
            sms.send_sms()
            logger.info('SMS: sending try, ID=%d' % sms.id)
        except:
            logger.error('SMS: sending failed, ID=%d' % sms.id)
    else:
        # or fake it
        sms.fake()
        logger.info('SMS: debug sending, ID=%d' % sms.id)


@app.task
def reset_attempts(user_id):
    """Reset user attempts"""
    from authorization import models as auth_models
    userlock_qs = auth_models.UserLock.objects.filter(user=user_id)
    # reset attempts
    if userlock_qs.exists():
        userlock_qs.first().reset_attempts()


@app.task
def not_completed_authorization(user_id):
    """Authorization was not completed"""
    from authorization import models as auth_models
    try:
        reset_attempts(user_id=user_id)
        auth_models.SMSCode.objects.decline_all_by_user(user_id=user_id)
    except:
        logger.info(f'ERROR: authorization was not completed for user {user_id}')


@app.task
def success_authorization(user_id, sms_code_id):
    """Finish of success authorization"""
    from authorization import models as auth_models
    try:
        reset_attempts(user_id=user_id)
        change_smscode_status(sms_code_id=sms_code_id, status=auth_models.SMSCode.ACTIVATED)
        auth_models.SMSCode.objects.decline_all_by_user(user=user_id)
    except:
        logger.info(f'ERROR: success authorization was not completed for user {user_id}')


@app.task
def change_smscode_status(sms_code_id, status):
    """Change SMSCode object status"""
    from authorization import models as auth_models
    smscode = auth_models.SMSCode.objects.get(id=sms_code_id)
    smscode.status = status
    smscode.save()


@app.task
def notify_friend_request(invited_id):
    """Notify user about new friend request"""
    from base import models as base_models
    from userprofile.models import FCMDevice
    notification = base_models.PushNotification.objects.create(
        user_id=invited_id,
        title=_('New friend request'),
        description=_('A new friend request has been received')
    )
    devices = FCMDevice.objects.filter(user_id=invited_id)
    if devices.exists():
        count = devices.send_message(**notification.get_push_dict())
        if count.get('success') > 0:
            logger.info(f'Users notified: {count.get("success")}')
        else:
            logger.info(f'Error was occurred when sending PUSH-notifications')


@app.task
def notify_chat_participants(sender_id, participants, room_id):
    """Notify user about new friend request"""
    from account import models as account_models
    from base import models as base_models
    from userprofile.models import FCMDevice

    for user_id in participants:
        # Get sender user object
        sender = account_models.User.objects.get(id=sender_id)
        # Check if user is online
        notification = base_models.PushNotification.objects.create(
            user_id=user_id,
            title=_('New message from chat'),
            description=_('User %s wrote a message') % sender.get_full_name()
        )
        devices = FCMDevice.objects.filter(user_id=user_id)
        if devices.exists():
            count = devices.send_message(**notification.get_push_dict(room_id=room_id))
            if count.get('success') > 0:
                notification.status = True
                notification.save()
                logger.info(f'Users notified: {count.get("success")}')
            else:
                logger.info(f'Error was occurred when sending PUSH-notifications. Failed: {count.get("failure")}')


@app.task
def notify_assistance_request(sender_id):
    """Notify users about assistance request"""
    from base import models as base_models
    from userprofile.models import FCMDevice
    devices = FCMDevice.objects.exclude(user_id=sender_id).filter(active=True)
    for device in devices:
        notification = base_models.PushNotification.objects.create(
            user=device.user,
            title=_('New assistance request'),
            description=_('New assistance request was published')
        )
        count = device.send_message(**notification.get_push_dict())
        if count.get('success') > 0:
            notification.status = True
            notification.save()
            logger.info(f'Users notified: {count.get("success")}')
        else:
            logger.info(f'Error was occurred when sending PUSH-notifications. Failed: {count.get("failure")}')

# Unused
# @app.task
# def notify_unread_messages():
#     """Notify users about unread messages"""
#     from base import models as base_models
#     from chat import models as chat_models
#     from fcm_django.models import FCMDevice
#
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
