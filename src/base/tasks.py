import logging

from base.models import (
    NewsletterComment,
    NewsletterLike,
    PushNotification,
)
from roadhelpbackend.celery import app
from userprofile.models import FCMDevice
from utils.push import send_push

logger = logging.getLogger("CELERY")


@app.task
def notify_new_newsletter(newsletter_id):
    """Notify user about new newsletter"""
    devices = FCMDevice.objects.filter(active=True)
    if not devices.exists():
        return

    notification = PushNotification.objects.make_new_newsletter_notification(  # noqa
        user=devices.first().user, newsletter=newsletter_id
    )
    result = send_push(devices, **notification.get_push_dict(model_id=newsletter_id))
    if result.get("success"):
        notification.status = True
        notification.sent_count = result["success"]
        notification.save()
        logger.info(f"Users notified for New Newsletter: {result['success']}")
    else:
        logger.info("Error when sending PUSH-notifications for New Newsletter.")


@app.task
def notify_new_newsletter_like(newsletter_like_id):
    """Notify user about new newsletter like"""
    like = NewsletterLike.objects.filter(id=newsletter_like_id).first()
    if not like:
        return
    initiator = like.owner
    user = like.newsletter.author
    if user == initiator or user is None or initiator is None:
        return

    notification = PushNotification.objects.make_newsletter_like_notification(  # noqa
        user=user, initiator=initiator
    )
    devices = FCMDevice.objects.filter(user_id=user.id)
    if not devices.exists():
        return

    result = send_push(devices, **notification.get_push_dict(model_id=like.newsletter.id))
    if result.get("success"):
        notification.status = True
        notification.sent_count = result["success"]
        notification.save()
        logger.info(f"User notified: {result['success']}")
    else:
        logger.info("Error when sending PUSH-notifications for newsletter like.")


@app.task
def notify_new_newsletter_comment(newsletter_comment_id):
    """Notify user about new newsletter comment"""
    comment = NewsletterComment.objects.filter(id=newsletter_comment_id).first()
    if not comment:
        return
    initiator = comment.author
    user = comment.newsletter.author
    if user == initiator or user is None or initiator is None:
        return

    notification = PushNotification.objects.make_newsletter_comment_notification(  # noqa
        user=user, initiator=initiator
    )
    devices = FCMDevice.objects.filter(user_id=user.id)
    if not devices.exists():
        return

    result = send_push(devices, **notification.get_push_dict(model_id=comment.newsletter.id))
    if result.get("success"):
        notification.status = True
        notification.sent_count = result["success"]
        notification.save()
        logger.info(f"User notified: {result['success']}")
    else:
        logger.info("Error when sending PUSH-notifications for newsletter comment.")
