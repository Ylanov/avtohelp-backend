import logging
import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings
from django.utils import timezone

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
    # Calls check_verification_sms_relevance() every 6 hours
    sender.add_periodic_task(crontab(hour=6),
                             check_verification_sms_relevance.s(),
                             name='Check verification SMS relevance')
    # Unused
    # sender.add_periodic_task(crontab(minute=settings.MESSAGES_UPDATE_PERIOD),
    #                          notify_unread_messages.s(),
    #                          name='Notify users about unread messages')


@app.task
def check_verification_sms_relevance():
    """Check verification SMS relevance"""
    from authorization import models as auth_models
    for sms_code in auth_models.SMSCode.objects.filter(status=auth_models.SMSCode.SENT):
        delta = (sms_code.created +
                 timezone.timedelta(seconds=settings.SMS_BLOCKING_PERIOD))
        if timezone.now() <= delta:
            sms_code.status = auth_models.SMSCode.DECLINED
            sms_code.save()


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
    notification = base_models.PushNotification.objects.make_friend_request_notification(user=invited_id)
    devices = FCMDevice.objects.filter(user_id=invited_id)
    if devices.exists():
        raw_result = devices.send_message(**notification.get_push_dict())
        result = raw_result if hasattr(raw_result, 'get') else {k: v for k, v in raw_result[0].items()}
        if result.get('success'):
            notification.status = True
            notification.sent_count = result.get('success')
            notification.save()
            logger.info(f'User notified: {result.get("success")}')
        else:
            logger.info(f'Error was occurred when sending PUSH-notifications')


@app.task
def notify_chat_participants(sender_id, room_id, participants):
    """Notify user about new friend request"""
    from account import models as account_models
    from chat import models as chat_models
    from base import models as base_models
    from userprofile.models import FCMDevice

    for user_id in participants:
        # Get sender user object
        sender = account_models.User.objects.get(id=sender_id)

        # Get participant obj
        participant = account_models.User.objects.get(id=user_id)

        # Get counter of unread messages
        unread_messages = chat_models.ChatRoom.objects.by_room(room_id=room_id)\
                                                      .annotate_unread_messages(user=participant)\
                                                      .first()\
                                                      .unread_messages

        # Check if user is online
        notification = base_models.PushNotification.objects.make_new_message_notification(
            user=user_id,
            sender=sender
        )
        devices = FCMDevice.objects.filter(user_id=user_id)
        if devices.exists():
            # Send PUSH-notification
            raw_result = devices.send_message(
                badge=unread_messages,
                **notification.get_push_dict(sender_id=sender.profile.id, room_id=room_id))

            result = raw_result if hasattr(raw_result, 'get') else {k: v for k, v in raw_result[0].items()}
            if result.get('success') > 0:
                notification.status = True
                notification.sent_count = result.get('success')
                notification.save()
                logger.info(f'Users notified: {result.get("success")}')
            else:
                logger.info(f'Error was occurred when sending PUSH-notifications. Failed: {result.get("failure")}')


@app.task
def notify_assistance_request(request_id):
    """Notify users about assistance request"""
    from base import models as base_models
    from order import models as order_models
    from userprofile.models import FCMDevice

    #  Settings
    singleton = base_models.PushNotificationConfiguration.get_solo()
    #  Assistance request
    request = order_models.AssistanceRequest.objects.get(id=request_id)

    """
    Get active devices
    
    Filter devices by active state
    .annotate_device_geo_position_relevance()
    annotate field that geo position updated not earlier than value that set in singleton object
    
    .annotate_device_distance_from_assistance_request(assistance_request=request)
    annotate field distance, that evaluate by this func Distance('profilelocation', assistance_request.location)
    
    .filter(distance__lte=singleton.radius)
    filter on it and check if annotated field value (annotated distance) is less or equal than radius in 
    singleton object 
    """
    devices = FCMDevice.objects.filter(active=True)\
        .annotate_device_geo_position_relevance()\
        .filter(geo_position_is_valid=True)\
        .annotate_device_distance_from_assistance_request(assistance_request=request)\
        .filter(distance__lte=singleton.radius) \
        .exclude(user=request.user)

    #  Sent PUSH-notifications for filtered users
    for device in devices:
        notification = base_models.PushNotification.objects.make_assistance_request_notification(user=device.user)
        raw_result = device.send_message(**notification.get_push_dict(request_id=request_id))
        result = raw_result if hasattr(raw_result, 'get') else {k: v for k, v in raw_result[0].items()}
        if result.get('success'):
            notification.status = True
            notification.sent_count = result.get('success')
            notification.save()
            logger.info(f'User notified: {result.get("success")}')
        else:
            logger.info(f'Error was occurred when sending PUSH-notifications')


@app.task
def read_messages(reader_id, room_id):
    """Set read flag is true by user"""
    from chat import models as chat_models
    qs = chat_models.ChatMessage.objects.exclude(chatreadmessage__user_id=reader_id)\
                                        .exclude(sender_id=reader_id)\
                                        .filter(room_id=room_id)\

    if qs.exists():
        for message in qs:
            chat_models.ChatReadMessage.objects.read(user_id=reader_id, message=message)


@app.task
def read_message(message_list, reader_id):
    """Set read flag is true by user"""
    from chat import models as chat_models
    qs = chat_models.ChatMessage.objects.exclude(chatreadmessage__user_id=reader_id)\
                                        .exclude(sender_id=reader_id)\
                                        .filter(id__in=message_list)
    if qs.exists():
        for message in qs:
            chat_models.ChatReadMessage.objects.read(user_id=reader_id, message=message)

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
