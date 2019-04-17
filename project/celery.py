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
    sender.add_periodic_task(crontab(minute=settings.MESSAGES_UPDATE_PERIOD),
                             notify_unread_messages.s(),
                             name='Notify users about unread messages')


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
def notify_unread_messages():
    """Notify users about unread messages"""
    from base import models as base_models
    from chat import models as chat_models
    from fcm_django.models import FCMDevice

    rooms = chat_models.ChatRoom.objects.all()
    for room in rooms:
        notify = list()
        for participant in room.participants.all():
            message_count = room.chatmessage_set.exclude(sender=participant).count()
            read_messages = chat_models.ChatReadMessage.objects.filter(user=participant).count()
            if (message_count - read_messages) > settings.LIMIT_UNREAD_MESSAGES:
                notify.append(participant)
            # for message in room.chatmessage_set.all():
            #     qs = chat_models.ChatReadMessage.objects.filter(message=message, user=participant)
            #     if not qs.exists():
            #         notify.append(participant)
        if notify:
            for user in notify:
                notification = base_models.PushNotification.objects.create(
                    user=user,
                    title=_('Unread messages'),
                    description=_('You have unread messages')
                )
                devices = FCMDevice.objects.filter(user=user)
                if devices.exists():
                    count = devices.send_message(**notification.get_push_dict())
                    if count.get('success') > 0:
                        notification.status = True
                        notification.save()
                        logger.info(f'Users notified: {count.get("success")}')
                    else:
                        logger.info(
                            f'Error was occurred when sending PUSH-notifications. Failed: {count.get("failure")}')
        notify.clear()
