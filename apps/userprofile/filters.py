import django_filters
from django.contrib.postgres.search import SearchQuery

from userprofile import models


class ProfileListFilterSet(django_filters.FilterSet):
    """ProfileList filter set."""

    search = django_filters.CharFilter(method='full_text_search')
    online = django_filters.BooleanFilter()
    friend = django_filters.BooleanFilter()

    class Meta:
        """Meta class."""

        model = models.Profile
        fields = [
            'online',
            'friend',
            'search',
        ]

    def full_text_search(self, queryset, name, value):
        if value:
            # Parse search parameters in value
            query_params = [item.strip() for item in value.split(' ')]
            # Full-text search
            qs = queryset.annotate_full_text_search().filter(
                search=SearchQuery(query_params[0]) |
                       SearchQuery(query_params[1] if len(query_params) == 2 else '') |
                       SearchQuery(query_params[2] if len(query_params) == 3 else '')
            )
            # If qs is empty find something
            if not qs.exists():
                qs = queryset.annotate_full_text_search().filter(search__icontains=value)
            return qs
        return queryset


class ProfileGalleryListFilterSet(django_filters.FilterSet):
    """ProfileGallery filter set."""

    person_id = django_filters.NumberFilter(field_name='profile__id')

    class Meta:
        """Meta class."""

        model = models.ProfileGallery
        fields = [
            'person_id',
        ]


class OutgoingRequestFilterSet(django_filters.FilterSet):
    """Outgoing friend request filter set."""

    person_id = django_filters.NumberFilter(field_name='invited__profile__id')

    class Meta:
        """Meta class."""

        model = models.FriendRequest
        fields = [
            'person_id',
        ]


class IncomingRequestFilterSet(django_filters.FilterSet):
    """Incoming friend request filter set."""

    person_id = django_filters.NumberFilter(field_name='owner__profile__id')

    class Meta:
        """Meta class."""

        model = models.FriendRequest
        fields = [
            'person_id',
        ]
