import logging

from account import models as account_models
from base.models import PushNotification
from chat.models import ChatMessage, ChatReadMessage, ChatRoom
from roadhelpbackend.celery import app
from userprofile.models import FCMDevice

logger = logging.getLogger("CELERY")


@app.task
def read_messages(reader_id, room_id):
    """Set read flag is true by user"""
    qs = (
        ChatMessage.objects.exclude(
            chatreadmessage__user_id=reader_id
        )
        .exclude(sender_id=reader_id)
        .filter(room_id=room_id)
    )
    if qs.exists():
        for message in qs:
            ChatReadMessage.objects.read(
                user_id=reader_id, message=message
            )


@app.task
def read_message(message_list, reader_id):
    """Set read flag is true by user"""

    qs = (
        ChatMessage.objects.exclude(
            chatreadmessage__user_id=reader_id
        )
        .exclude(sender_id=reader_id)
        .filter(id__in=message_list)
    )
    if qs.exists():
        for message in qs:
            ChatReadMessage.objects.read(
                user_id=reader_id, message=message
            )


@app.task
def notify_chat_participants(sender_id, room_id, participants):
    """Notify user about new friend request"""

    for user_id in participants:
        # Get sender user object
        sender = account_models.User.objects.get(id=sender_id)

        # Get participant obj
        participant = account_models.User.objects.get(id=user_id)

        # Get counter of unread messages
        unread_messages = (
            ChatRoom.objects.by_room(room_id=room_id)
            .annotate_unread_messages(user=participant)
            .first()
            .unread_messages
        )

        # Check if user is online
        notification = (
            PushNotification.objects.make_new_message_notification(
                user=user_id, sender=sender
            )
        )
        devices = FCMDevice.objects.filter(user_id=user_id)
        if devices.exists():
            # Send PUSH-notification
            raw_result = devices.send_message(
                badge=unread_messages,
                **notification.get_push_dict(
                    sender_id=sender.profile.id, room_id=room_id
                ),
            )

            result = (
                raw_result
                if hasattr(raw_result, "get")
                else {k: v for k, v in raw_result[0].items()}
            )
            if result.get("success") > 0:
                notification.status = True
                notification.sent_count = result.get("success")
                notification.save()
                logger.info(f'Users notified: {result.get("success")}')
            else:
                logger.info(
                    f'Error was occurred when sending PUSH-notifications. Failed: {result.get("failure")}'  # noqa
                )
