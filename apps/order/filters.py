import django_filters
from . import models


class AssistanceRequestFitlerSet(django_filters.FilterSet):
    """Filters for AssistanceRequest"""

    distance = django_filters.NumberFilter()

    class Meta:
        """Meta class"""
        model = models.AssistanceRequest
        fields = [
            'user', 'status', 'distance'
        ]
