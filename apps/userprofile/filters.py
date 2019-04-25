import django_filters
from userprofile import models
from django.contrib.postgres.search import SearchQuery
from django.db import models as db_models

class ProfileListFilterSet(django_filters.FilterSet):
    """ProfileList filter set."""

    # first_name = django_filters.CharFilter(method='by_first_name')
    # last_name = django_filters.CharFilter(method='by_last_name')
    license_plate = django_filters.CharFilter(method='by_license_plate')

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

            # 'first_name',
            # 'last_name',
            'license_plate'
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

    # def by_first_name(self, queryset, name, value):
    #     if value:
    #         qs = queryset.filter(first_name__contains=value)
    #         if not qs.exists() or len(value) > 3:
    #             qs = queryset.filter(first_name__icontains=value)
    #         return qs
    #     return queryset
    #
    # def by_last_name(self, queryset, name, value):
    #     if value:
    #         qs = queryset.filter(last_name__contains=value)
    #         if not qs.exists() or len(value) > 3:
    #             qs = queryset.filter(last_name__icontains=value)
    #         return qs
    #     return queryset

    def by_license_plate(self, queryset, name, value):
        if value:
            qs = queryset.filter(user__profilecar__license_plate__contains=value).distinct()
            if not qs.exists() or len(value) > 3:
                qs = queryset.filter(user__profilecar__license_plate__icontains=value).distinct()
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
