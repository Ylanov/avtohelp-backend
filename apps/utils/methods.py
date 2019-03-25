import random

from channels.db import database_sync_to_async
from django.conf import settings
from django.utils import timezone

from chat import models as chat_models


def generate_image_name():
    """Generate code method."""
    return '%06d' % random.randint(0, 999999)


def image_path(instance, filename):
    """Determine avatar path method."""
    filename = '%s.jpeg' % generate_image_name()
    return 'image/%s/%s/%s' % (
        instance._meta.model_name,
        timezone.now().strftime(settings.REST_DATE_FORMAT),
        filename)


def generate_sms_code(length=settings.SMS_CODE_LENGTH):
    from random import randint
    code = ''
    for i in range(length):
        code += str(randint(0, 9))
    return code


def get_exception_body(exception):
    if hasattr(exception, 'extended_status_code'):
        return dict(detail=exception.default_detail, status_code=exception.extended_status_code)
    return dict(detail=exception.default_detail)


@database_sync_to_async
def create_chat_message(sender: object, room: int, message: str):
    # Get room
    room = chat_models.ChatRoom.objects.get(id=room)
    # Make a record in the DB
    obj = chat_models.ChatMessage.objects.create(sender=sender, room=room, message=message)
    obj.save()
    return obj
