from rest_framework import generics
from chat.serializers import current as serializers
from chat import models
from account.models import User


class MessageListView(generics.ListAPIView):
    """MessageList view"""

    serializer_class = serializers.MessageListSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        sender = generics.get_object_or_404(User.objects.all(), pk=self.kwargs.get('sender'))
        receiver = generics.get_object_or_404(User.objects.all(), pk=self.kwargs.get('receiver'))
        return models.Message.objects.filter(sender=sender, receiver=receiver)


class MessageCreateView(generics.CreateAPIView):
    """Message create view"""

    serializer_class = serializers.MessageCreateSerializer
    queryset = models.Message.objects.all()
