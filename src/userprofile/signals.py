from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.gis import measure, geos
from django.db.models import Q
from .models import ProfileLocation

from order.models import AssistanceRequest
from order.choices import AVAILABLE


@receiver(pre_save, sender=AssistanceRequest)
def check_nearby_assistance_requests_after_update_location(sender, instance, **kwargs):
    distance_from_point = {"km": 5}

    if instance.status == AVAILABLE:
        current_point = geos.fromstr("POINT(%s %s)" % (64.5490547, 40.5304254))

        exclude_blocked_users = Q(
            user_id__ne=instance.user.blacklist_owner.all(),
        )

        shops = ProfileLocation.gis.filter(
            location__distance_lte=(current_point, measure.D(**distance_from_point)),
        ).exclude(
            exclude_blocked_users,
            user__in=[instance.user],
        )

        print(shops)
