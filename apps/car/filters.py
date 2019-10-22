import django_filters
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance

from car import models


class CarListFilterSet(django_filters.FilterSet):
    """Filters for CarList"""

    mark_name = django_filters.CharFilter(method='by_mark_name')
    model_name = django_filters.CharFilter(method='by_model_name')

    class Meta:
        """Meta class."""

        model = models.Car
        fields = [
            'mark_name',
            'model_name',
        ]

    def by_mark_name(self, queryset, name, value):
        if value:
            qs = queryset.filter(mark__name=value).distinct('id')
            if not qs.exists() or len(value) > 3:
                qs = queryset.filter(mark__name__icontains=value).distinct('id')
            return qs
        return queryset

    def by_model_name(self, queryset, name, value):
        if value:
            qs = queryset.filter(car_model__name__contains=value).distinct('id')
            if not qs.exists() or len(value) > 3:
                qs = queryset.filter(car_model__name__icontains=value).distinct('id')
            return qs
        return queryset


class CarColorFilterSet(django_filters.FilterSet):
    """Filters for CarList"""

    color_name = django_filters.CharFilter(method='by_color_name')

    class Meta:
        """Meta class."""

        model = models.CarColor
        fields = [
            'color_name',
        ]

    def by_color_name(self, queryset, name, value):
        if value:
            qs = queryset.filter(name=value)
            if not qs.exists() or len(value) > 3:
                qs = queryset.filter(name__icontains=value)
            return qs
        return queryset


class CarMarkListFilterSet(django_filters.FilterSet):
    """Filters for CarMark"""

    model_name = django_filters.CharFilter(method='by_model_name')
    mark_name = django_filters.CharFilter(method='by_mark_name')

    class Meta:
        """Meta class."""

        model = models.CarMark
        fields = [
            'model_name',
            'mark_name'
        ]

    def by_model_name(self, queryset, name, value):
        if value:
            qs = queryset.filter(carmodel__name__contains=value).distinct('id')
            if not qs.exists() or len(value) > 3:
                qs = queryset.filter(carmodel__name__icontains=value).distinct('id')
            return qs
        return queryset

    def by_mark_name(self, queryset, name, value):
        if value:
            qs = queryset.filter(name__contains=value).distinct('id')
            if not qs.exists() or len(value) > 3:
                qs = queryset.filter(name__icontains=value).distinct('id')
            return qs
        return queryset


class CarModelListFilterSet(django_filters.FilterSet):
    """Filters for CarModel"""

    mark_name = django_filters.CharFilter(method='by_mark_name')
    model_name = django_filters.CharFilter(method='by_model_name')

    class Meta:
        """Meta class."""

        model = models.CarModel
        fields = [
            'mark_name',
            'model_name'
        ]

    def by_mark_name(self, queryset, name, value):
        if value:
            qs = queryset.filter(mark__name=value).distinct('id')
            if not qs.exists() or len(value) > 3:
                qs = queryset.filter(mark__name__icontains=value).distinct('id')
            return qs
        return queryset

    def by_model_name(self, queryset, name, value):
        if value:
            qs = queryset.filter(name=value).distinct('id')
            if not qs.exists() or len(value) > 3:
                qs = queryset.filter(name__icontains=value).distinct('id')
            return qs
        return queryset


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
