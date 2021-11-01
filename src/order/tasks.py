import logging

from django.conf import settings
from django.utils import timezone

from order.choices import EXPIRED
from order.models import AssistanceRequest
from roadhelpbackend.celery import app

logger = logging.getLogger("CELERY")


@app.task
def check_request_relevance():
    """Check relevance of assistance requests"""

    available_requests = AssistanceRequest.objects.exclude(status=EXPIRED)

    if available_requests.exists():
        for request in available_requests:
            expired_date = request.created + timezone.timedelta(
                minutes=settings.REQUEST_RELEVANCE
            )
            if timezone.now() >= expired_date:
                request.status = EXPIRED
                request.save()


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
    if devices.exists():
        notification = PushNotification.objects.make_assistance_request_notification(  # noqa
            user=devices.first().user
        )
        raw_result = devices.send_message(
            **notification.get_push_dict(request_id=request_id)
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
            logger.info(f'Users notified: {result.get("success")}')
        else:
            logger.info("Error was occurred when sending PUSH-notifications")
