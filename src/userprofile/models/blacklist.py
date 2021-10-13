from django.db import models
from django.utils.translation import ugettext_lazy as _

from utils.mixins import BaseMixin

from ..managers import BlackListManager
from ..query_set import BlackListQuerySet


class BlackList(BaseMixin):
    """BlackList model"""

    owner = models.ForeignKey(
        "account.User",
        verbose_name=_("Owner"),
        related_name="blacklist_owner",
        on_delete=models.CASCADE,
    )
    foe = models.ForeignKey(
        "account.User",
        verbose_name=_("Foe"),
        related_name="blacked_user",
        on_delete=models.CASCADE,
    )

    objects = BlackListManager.from_queryset(BlackListQuerySet)()

    class Meta:
        """Meta-class"""

        verbose_name = _("Black list")
        verbose_name_plural = _("Black lists")
        unique_together = (
            "owner",
            "foe",
        )
