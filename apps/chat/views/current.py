from rest_framework import generics
from chat.serializers import current as serializers
from chat import models
from account.models import User
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json


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


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })

def index(request):
    return render(request, 'chat/index.html', {})