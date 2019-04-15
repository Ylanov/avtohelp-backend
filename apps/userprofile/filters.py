import django_filters
from userprofile import models


class ProfileListFilterSet(django_filters.FilterSet):
    """ProfileList filter set."""

    online = django_filters.BooleanFilter()
    friend = django_filters.BooleanFilter()
    search = django_filters.CharFilter(method='search_filter')

    class Meta:
        """Meta class."""

        model = models.Profile
        fields = [
            'online',
            'friend',
            'search'
        ]

    def search_filter(self, queryset, name, value):
        """Full text search"""
        qs = queryset.annotate_full_search().filter(search=value).distinct(
            'created', 'first_name', 'last_name')
        if not qs.exists() and len(value) > 3:
            qs = queryset.annotate_full_search().filter(search__icontains=value).distinct(
                'created', 'first_name', 'last_name')
        return qs


class ProfileGalleryListFilterSet(django_filters.FilterSet):
    """ProfileGallery filter set."""
    class Meta:
        """Meta class."""

        model = models.ProfileGallery
        fields = [
            'profile',
        ]


class OutgoingRequestFilterSet(django_filters.FilterSet):
    """Outgoing friend request filter set."""

    person = django_filters.NumberFilter(field_name='invited__profile')

    class Meta:
        """Meta class."""

        model = models.FriendRequest
        fields = [
            'person',
        ]


class IncomingRequestFilterSet(django_filters.FilterSet):
    """Incoming friend request filter set."""

    person = django_filters.NumberFilter(field_name='owner__profile')

    class Meta:
        """Meta class."""

        model = models.FriendRequest
        fields = [
            'person',
        ]
