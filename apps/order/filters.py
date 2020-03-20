import django_filters
from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django_filters import rest_framework as filters

from . import models


class DistanceOrderingFilter(filters.OrderingFilter):
    """Ordering by distance"""
    def filter(self, qs, value):
        if value:
            return qs.order_by(value[0])
        return qs


class AssistanceRequestRadiusFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """Filter by distance"""

    def filter(self, qs, value):
        if value:
            x, y = float(value[0]), float(value[1])
            point = Point(x, y, srid=4326)
            if settings.DEFAULT_REQUEST_RADIUS:
                return qs.filter(location__distance_lte=(point, Distance(m=settings.DEFAULT_REQUEST_RADIUS)))
            else:
                return qs.filter(location__distance_lte=(point, Distance(
                    m=float(value[2]) if len(value) == 3 else settings.DEFAULT_REQUEST_RADIUS)))
        return qs


class AssistanceRequestFitlerSet(django_filters.FilterSet):
    """Filters for AssistanceRequest"""

    profile_id = django_filters.NumberFilter(field_name='user__profile__id')
    coordinates = AssistanceRequestRadiusFilter()
    o = DistanceOrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('distance', 'distance'),
        ),

        # labels do not need to retain order
        field_labels={
            'distance': 'Distance',
        }
    )

    class Meta:
        """Meta class"""
        model = models.AssistanceRequest
        fields = [
            'profile_id',
            'coordinates',
        ]
