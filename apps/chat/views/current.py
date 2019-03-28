import json

from django.shortcuts import render
from django.utils.safestring import mark_safe
from rest_framework import generics, views
from rest_framework.permissions import AllowAny
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response

from chat import models, filters, permissions
from chat.serializers import current as serializers


class ChatMessageListView(generics.ListAPIView):
    """MessageList view"""
    serializer_class = serializers.ChatMessageListSerializer
    queryset = models.ChatMessage.objects.all()
    permission_classes = (permissions.ChatMessagePermission,)
    filter_class = filters.ChatMessageFilterSet
    pagination_class = CursorPagination

    def get_queryset(self):
        """Override get_queryset method"""
        return models.ChatMessage.objects.filter(room=self.kwargs.get('pk'))


class ChatMessageCountView(views.APIView):
    """MessageList view"""

    def get(self, request, *args, **kwargs):
        """Get count of assistance requests"""
        return Response({
            'count': models.ChatMessage.objects.filter(room=kwargs.get('pk')).count()})


class ChatRoomDetailView(generics.RetrieveAPIView):
    """MessageList view"""
    serializer_class = serializers.ChatRoomDetailSerializer
    permission_classes = (permissions.ChatMessagePermission,)
    queryset = models.ChatRoom.objects.all()


class ChatRoomListView(generics.ListAPIView):
    """Chat room list view"""
    serializer_class = serializers.ChatRoomListSerializer
    filter_class = filters.ChatRoomListFilterSet

    def get_queryset(self):
        """Override get queryset method"""
        return models.ChatRoom.objects.by_participant(participant=self.request.user)


class ChatView(generics.GenericAPIView):
    """Private room view"""

    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        """Override get method."""

        return render(request, 'chat/private.html', {
            'rooms': models.ChatRoom.objects.by_participant(participant=self.request.user)
        })


class PrivateChatRoomCreateView(generics.CreateAPIView):
    """Create chat room"""

    serializer_class = serializers.PrivateChatRoomCreateSerializer
