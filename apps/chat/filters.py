import django_filters
from chat import models
from userprofile import models as profile_models


class ChatMessageFilterSet(django_filters.FilterSet):
    """Filters for ChatMessage"""

    read = django_filters.BooleanFilter()
    created = django_filters.DateFromToRangeFilter()

    class Meta:
        """Meta class."""

        model = models.ChatMessage
        fields = [
            'created', 'read'
        ]


class ChatRoomListFilterSet(django_filters.FilterSet):
    """Filters for model ChatRoom"""

    participant = django_filters.filters.ModelChoiceFilter(
        field_name='participants__profile',
        to_field_name='id',
        queryset=profile_models.Profile.objects.all(),
    )
    is_public = django_filters.BooleanFilter()

    class Meta:
        """Meta class"""
        model = models.ChatRoom
        fields = [
            'is_public', 'participants'
        ]