import logging

from base.models import PushNotification
from roadhelpbackend.celery import app
from userprofile.models import FCMDevice

logger = logging.getLogger("CELERY")


@app.task
def notify_friend_request(invited_id):
    """Notify user about new friend request"""

    notification = PushNotification.objects.make_friend_request_notification(
        user=invited_id
    )

    devices = FCMDevice.objects.filter(user_id=invited_id)

    if devices.exists():
        raw_result = devices.send_message(**notification.get_push_dict())
        result = (
            raw_result
            if hasattr(raw_result, "get")
            else {k: v for k, v in raw_result[0].items()}
        )
        if result.get("success"):
            notification.status = True
            notification.sent_count = result.get("success")
            notification.save()
            logger.info(f'User notified: {result.get("success")}')
        else:
            logger.info("Error was occurred when sending PUSH-notifications")
