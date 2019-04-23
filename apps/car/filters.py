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

    search = django_filters.CharFilter(method='search_filter')
    model_id = django_filters.NumberFilter(field_name='carmodel__id')

    class Meta:
        """Meta class."""

        model = models.CarMark
        fields = [
            'search',
            'name',
            'model_id'
        ]

    def search_filter(self, queryset, name, value):
        """Full text search"""
        qs = queryset.annotate_full_search().filter(search=value)
        if not qs.exists() or len(value) > 3:
            qs = queryset.annotate_full_search().filter(search__icontains=value)
        return qs


class CarModelListFilterSet(django_filters.FilterSet):
    """Filters for CarModel"""

    mark_id = django_filters.NumberFilter(field_name='mark__id')
    search = django_filters.CharFilter(method='search_filter')

    class Meta:
        """Meta class."""

        model = models.CarModel
        fields = [
            'search',
            'name',
            'mark_id',
        ]

    def search_filter(self, queryset, name, value):
        """Full text search"""
        qs = queryset.annotate_full_search().filter(search=value)
        if not qs.exists() or len(value) > 3:
            qs = queryset.annotate_full_search().filter(search__icontains=value)
        return qs


class CenterFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """Filter by distance"""

    def filter(self, qs, value):
        if value:
            center_x = float(value[0])
            center_y = float(value[1])
            radius = int(value[2])

            center = Point(x=center_x, y=center_y, srid=4326)
            return qs.filter(location__distance_lte=(center, Distance(m=radius)))
        return qs


class ServiceStationsFilterSet(django_filters.FilterSet):
    """Filters for ServiceStations"""

    from_center = CenterFilter()
    distance = django_filters.NumberFilter()
    icon_exists = django_filters.BooleanFilter()

    class Meta:
        """Meta class"""
        model = models.CarService
        fields = [
            'category_id',
            'from_center',
            'distance',
            'icon_exists'
        ]
