import django_filters
from car import models


class CarListFilterSet(django_filters.FilterSet):
    """Filters for CarList"""

    mark_name = django_filters.CharFilter(field_name='mark__name')
    model_name = django_filters.CharFilter(field_name='car_model__name')

    class Meta:
        """Meta class."""

        model = models.Car
        fields = [
            'mark_name', 'model_name',
            'car_model', 'mark'
        ]


class CarMarkListFilterSet(django_filters.FilterSet):
    """Filters for CarMark"""

    model_name = django_filters.CharFilter(field_name='carmodel__name')
    model_id = django_filters.NumberFilter(field_name='carmodel__id')

    class Meta:
        """Meta class."""

        model = models.CarMark
        fields = [
            'model_name', 'model_id',
        ]


class CarModelListFilterSet(django_filters.FilterSet):
    """Filters for CarModel"""

    mark_name = django_filters.CharFilter(field_name='mark__name')
    mark_id = django_filters.NumberFilter(field_name='mark__id')

    class Meta:
        """Meta class."""

        model = models.CarModel
        fields = [
            'mark_name', 'mark_id',
        ]
