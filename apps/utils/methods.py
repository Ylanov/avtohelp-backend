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


# This decorator turns this function from a synchronous function into an async one
# we can call from our async consumers, that handles Django DBs correctly.
# For more, see http://channels.readthedocs.io/en/latest/topics/databases.html
@database_sync_to_async
def get_room_or_error(initiator=None, participant=None, is_public=False):
    """
    Tries to fetch a room for the user.
    """
    return chat_models.ChatRoom.objects.get_or_create(initiator, participant, is_public)
