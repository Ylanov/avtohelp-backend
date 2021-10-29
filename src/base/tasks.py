import logging

from base.models import (
    NewsletterComment,
    NewsletterLike,
    PushNotification,
)
from roadhelpbackend.celery import app
from userprofile.models import FCMDevice

logger = logging.getLogger("CELERY")


@app.task
def notify_new_newsletter(newsletter_id):
    """Notify user about new newsletter"""

    devices = FCMDevice.objects.filter(active=True)

    # send bulk push message for filtered users
    if devices.exists():
        notification = (
            PushNotification.objects.make_new_newsletter_notification(  # noqa
                user=devices.first().user, newsletter=newsletter_id
            )
        )
        raw_result = devices.send_message(
            **notification.get_push_dict(model_id=newsletter_id)
        )
        result = (
            raw_result
            if hasattr(raw_result, "get")
            else {k: v for k, v in raw_result[0].items()}
        )
        if result.get("success"):
            notification.status = True
            notification.sent_count = result.get("success")
            notification.save()
            logger.info(
                f'User notified for New Newsletter: {result.get("success")}'
            )
        else:
            logger.info(
                "Error was occurred when sending PUSH-notifications for New Newsletter."  # noqa
            )


@app.task
def notify_new_newsletter_like(newsletter_like_id):
    """Notify user about new newsletter like"""

    like = NewsletterLike.objects.filter(id=newsletter_like_id).first()
    initiator = like.owner
    user = like.newsletter.author

    if user == initiator:
        return None

    if user is not None and initiator is not None:
        notification = base_models.PushNotification.objects.make_newsletter_like_notification(  # noqa
            user=user, initiator=initiator
        )
        devices = FCMDevice.objects.filter(user_id=user.id)
        if devices.exists():
            raw_result = devices.send_message(
                **notification.get_push_dict(model_id=like.newsletter.id)
            )
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
                logger.info(
                    "Error was occurred when sending PUSH-notifications"
                )


@app.task
def notify_new_newsletter_comment(newsletter_comment_id):
    """Notify user about new newsletter comment"""

    comment = NewsletterComment.objects.filter(
        id=newsletter_comment_id
    ).first()
    initiator = comment.author
    user = comment.newsletter.author

    if user == initiator:
        return None

    if user is not None and initiator is not None:
        notification = base_models.PushNotification.objects.make_newsletter_comment_notification(  # noqa
            user=user, initiator=initiator
        )
        devices = FCMDevice.objects.filter(user_id=user.id)
        if devices.exists():
            raw_result = devices.send_message(
                **notification.get_push_dict(model_id=comment.newsletter.id)
            )
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
                logger.info(
                    "Error was occurred when sending PUSH-notifications"
                )
