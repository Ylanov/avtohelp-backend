from django.utils.translation import gettext_lazy as _

EXPIRED = 0
AVAILABLE = 1
CANCELED = 2

STATUS_CHOICES = (
    (AVAILABLE, _("Assistance request is available")),
    (EXPIRED, _("Assistance request was expired")),
    (CANCELED, _("Assistance request was canceled")),
)
