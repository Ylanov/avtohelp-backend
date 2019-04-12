import django_filters
from . import models


class AssistanceRequestFitlerSet(django_filters.FilterSet):
    """Filters for AssistanceRequest"""

    distance = django_filters.RangeFilter()
    profile_id = django_filters.NumberFilter(field_name='user__profile__id')

    class Meta:
        """Meta class"""
        model = models.AssistanceRequest
        fields = [
            'profile_id',
            'distance'
        ]
