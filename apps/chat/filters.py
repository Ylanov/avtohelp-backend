import django_filters
from chat import models


class ChatMessageFilterSet(django_filters.FilterSet):
    """Filters for CarList"""

    first_name = django_filters.CharFilter(field_name='sender__profile__first_name')
    last_name = django_filters.CharFilter(field_name='sender__profile__last_name')
    middle_name = django_filters.CharFilter(field_name='sender__profile__middle_name')

    class Meta:
        """Meta class."""

        model = models.ChatMessage
        fields = [
            'sender', 'first_name', 'last_name', 'middle_name'
        ]
