import logging

from django.conf import settings
from django.utils import timezone

from order.choices import EXPIRED
from order.models import AssistanceRequest
from roadhelpbackend.celery import app
from utils.push import send_push

logger = logging.getLogger("CELERY")


@app.task
def check_request_relevance():
    """Mark assistance requests that have exceeded REQUEST_RELEVANCE as EXPIRED.

    Single SQL UPDATE — previously this iterated per-row (N+1).
    """
    cutoff = timezone.now() - timezone.timedelta(minutes=settings.REQUEST_RELEVANCE)
    AssistanceRequest.objects.exclude(status=EXPIRED).filter(
        created__lte=cutoff
    ).update(status=EXPIRED)


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
    annotate field that geo position updated not earlier 
    than value that set in singleton object

    .annotate_device_distance_from_assistance_request(assistance_request=request)
    annotate field distance, that evaluate by 
    this func Distance('profilelocation', assistance_request.location)

    .filter(distance__lte=singleton.radius)
    filter on it and check if annotated field value (annotated distance) 
    is less or equal than radius in singleton object 
    """
    devices = (
        FCMDevice.objects.filter(active=True)
        .annotate_device_geo_position_relevance()
        .filter(geo_position_is_valid=True)
        .annotate_device_distance_from_assistance_request(
            assistance_request=request
        )
        .filter(distance__lte=singleton.radius)
        .exclude(user=request.user)
    )

    # send bulk push message for filtered users
    if not devices.exists():
        return

    notification = base_models.PushNotification.objects.make_assistance_request_notification(  # noqa
        user=devices.first().user
    )
    result = send_push(devices, **notification.get_push_dict(request_id=request_id))
    if result.get("success"):
        notification.status = True
        notification.sent_count = result["success"]
        notification.save()
        logger.info(f"Users notified: {result['success']}")
    else:
        logger.info("Error when sending PUSH-notifications for assistance request.")
