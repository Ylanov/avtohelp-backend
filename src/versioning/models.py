from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel

from utils.mixins import BaseMixin


class RemoteServer(SingletonModel):
    url = models.URLField(blank=True, null=True, default=None)

    def __str__(self):
        return u"Remote Server"

    class Meta:
        verbose_name = _("Remote Server")


class Version(BaseMixin):

    version = models.CharField(
        _("Version"), max_length=6, unique=True, help_text=_("Example: 1.0.0")
    )
    active = models.BooleanField(_("Active"), default=False)

    def __str__(self):
        return self.version

    class Meta:
        verbose_name = _("Version")
        verbose_name_plural = _("Versions")
