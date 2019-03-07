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

