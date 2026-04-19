import logging

from base.models import PushNotification
from roadhelpbackend.celery import app
from userprofile.models import FCMDevice
from utils.push import send_push

logger = logging.getLogger("CELERY")


@app.task
def notify_friend_request(invited_id):
    """Notify user about new friend request"""
    notification = PushNotification.objects.make_friend_request_notification(
        user=invited_id
    )
    devices = FCMDevice.objects.filter(user_id=invited_id)
    if not devices.exists():
        return

    result = send_push(devices, **notification.get_push_dict())
    if result.get("success"):
        notification.status = True
        notification.sent_count = result["success"]
        notification.save()
        logger.info(f"User notified: {result['success']}")
    else:
        logger.info("Error when sending PUSH-notifications for friend request.")
