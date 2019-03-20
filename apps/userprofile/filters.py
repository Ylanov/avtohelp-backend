import django_filters
from userprofile import models


class ProfileListFilterSet(django_filters.FilterSet):
    """Med org filter set."""

    license_plate = django_filters.CharFilter(field_name='user__car__license_plate')

    class Meta:
        """Meta class."""

        model = models.Profile
        fields = [
            'first_name', 'last_name', 'middle_name', 'license_plate',
        ]
