import logging
import os

from celery import Celery

logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roadhelpbackend.settings")

broker_transport_options = {
    "is_secure": True,
}

app = Celery(
    "roadhelpbackend",
)

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.update(
    CELERYD_HIJACK_ROOT_LOGGER=False,
)

app.conf.broker_transport_options = broker_transport_options

app.autodiscover_tasks()
