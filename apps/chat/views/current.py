import json

from django.shortcuts import render
from django.utils.safestring import mark_safe
from rest_framework import generics
from rest_framework.permissions import AllowAny

from chat import models, filters, permissions
from chat.serializers import current as serializers


class ChatMessageListView(generics.ListAPIView):
    """MessageList view"""
    serializer_class = serializers.ChatMessageListSerializer
    queryset = models.ChatMessage.objects.all()
    permission_classes = (permissions.ChatMessagePermission,)
    filter_class = filters.ChatMessageFilterSet


class ChatRoomDetailView(generics.RetrieveAPIView):
    """MessageList view"""
    serializer_class = serializers.ChatRoomDetailSerializer
    permission_classes = (permissions.ChatMessagePermission,)
    queryset = models.ChatRoom.objects.all()


class ChatRoomListView(generics.ListAPIView):
    """Chat room list view"""
    serializer_class = serializers.ChatRoomListSerializer

    def get_queryset(self):
        """Override get queryset method"""
        return models.ChatRoom.objects.by_participant(participant=self.request.user)


class ChatRoomPrivateView(generics.GenericAPIView):
    """Private room view"""

    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        """Override get method."""
        return render(request, 'chat/private.html', {
            'room_json': mark_safe(json.dumps(kwargs.get('pk')))
        })


class PrivateChatRoomCreateView(generics.CreateAPIView):
    """Create chat room"""

    serializer_class = serializers.PrivateChatRoomCreateSerializer
