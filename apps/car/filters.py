import django_filters
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance

from car import models


class CarListFilterSet(django_filters.FilterSet):
    """Filters for CarList"""

    mark_name = django_filters.CharFilter(field_name='mark__name')
    model_name = django_filters.CharFilter(field_name='car_model__name')
    model_id = django_filters.NumberFilter(field_name='car_model')
    mark_id = django_filters.NumberFilter(field_name='mark')

    class Meta:
        """Meta class."""

        model = models.Car
        fields = [
            'mark_name',
            'model_name',
            'model_id',
            'mark_id'
        ]


class CarColorFilterSet(django_filters.FilterSet):
    """Filters for CarList"""

    class Meta:
        """Meta class."""

        model = models.CarColor
        fields = [
            'name',
        ]


class CarMarkListFilterSet(django_filters.FilterSet):
    """Filters for CarMark"""

    model_name = django_filters.CharFilter(field_name='carmodel__name')
    model_id = django_filters.NumberFilter(field_name='carmodel__id')

    class Meta:
        """Meta class."""

        model = models.CarMark
        fields = [
            'name',
            'model_name',
            'model_id',
        ]


class CarModelListFilterSet(django_filters.FilterSet):
    """Filters for CarModel"""

    mark_name = django_filters.CharFilter(field_name='mark__name')
    mark_id = django_filters.NumberFilter(field_name='mark__id')

    class Meta:
        """Meta class."""

        model = models.CarModel
        fields = [
            'name',
            'mark_name',
            'mark_id',
        ]


class CenterFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """Filter by distance"""

    def filter(self, qs, value):
        if value:
            center_x = float(value[0])
            center_y = float(value[1])
            radius = int(value[2])

            center = Point(center_x, center_y, srid=4326)
            return qs.filter(location__distance_lte=(center, Distance(m=radius)))
        return qs


class ServiceStationsFilterSet(django_filters.FilterSet):
    """Filters for ServiceStations"""

    from_center = CenterFilter()
    distance = django_filters.NumberFilter()

    class Meta:
        """Meta class"""
        model = models.CarService
        fields = [
            'category',
            'from_center',
            'distance'
        ]
