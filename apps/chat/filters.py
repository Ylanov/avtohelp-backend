import django_filters
from chat import models
from userprofile import models as profile_models


class ChatMessageFilterSet(django_filters.FilterSet):
    """Filters for ChatMessage"""

    first_name = django_filters.CharFilter(field_name='sender__profile__first_name')
    last_name = django_filters.CharFilter(field_name='sender__profile__last_name')
    middle_name = django_filters.CharFilter(field_name='sender__profile__middle_name')

    class Meta:
        """Meta class."""

        model = models.ChatMessage
        fields = [
            'sender', 'first_name', 'last_name', 'middle_name'
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