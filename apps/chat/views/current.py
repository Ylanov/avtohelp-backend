import json

from django.shortcuts import render
from django.utils.safestring import mark_safe
from rest_framework import generics

from account.models import User
from chat import models
from chat.serializers import current as serializers


class MessageListView(generics.ListAPIView):
    """MessageList view"""
    serializer_class = serializers.MessageListSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        sender = generics.get_object_or_404(User.objects.filter(is_active=True), pk=self.kwargs.get('sender'))
        receiver = generics.get_object_or_404(User.objects.filter(is_active=True), pk=self.kwargs.get('receiver'))
        return models.ChatMessage.objects.filter(sender=sender, receiver=receiver)


class ChatRoomListView(generics.ListAPIView):
    """Chat room list view"""
    serializer_class = serializers.ChatRoomListSerializer

    def get_queryset(self):
        """Override get queryset method"""
        return models.ChatRoom.objects.by_participant(participant=self.request.user)


class ChatRoomPrivateView(generics.GenericAPIView):
    """Private room view"""

    def get(self, request, *args, **kwargs):
        """Override get method."""
        return render(request, 'chat/private.html', {
            'room_json': mark_safe(json.dumps(kwargs.get('room')))
        })


class ChatRoomCreateView(generics.CreateAPIView):
    """Create chat room"""

    serializer_class = serializers.ChatRoomCreateSerializer
