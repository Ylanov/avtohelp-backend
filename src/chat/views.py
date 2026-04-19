from django.db.models import Q
from django.shortcuts import render
from rest_framework import (
    generics,
    status,
    views,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from utils.paginations import (
    ChatCursorPagination,
    ProjectCursorPagination,
)

from . import (
    filters,
    models,
    permissions,
)
from .serializers import current as serializers


class ChatMessageListView(generics.ListAPIView):
    """MessageList view"""

    serializer_class = serializers.ChatMessageListSerializer
    permission_classes = (permissions.ChatMessagePermission,)
    filter_class = filters.ChatMessageFilterSet
    pagination_class = ProjectCursorPagination

    def get_queryset(self):
        """Override get_queryset method"""
        return (
            models.ChatMessage.objects.filter(room=self.kwargs.get("pk"))
            .annotate_read_status(user=self.request.user)
            .distinct()
        )


class ChatReadMessageView(generics.CreateAPIView):
    """Create read message objects"""

    serializer_class = serializers.ChatReadMessageSerializer
    permission_classes = (permissions.ChatMessagePermission,)

    def create(self, request, *args, **kwargs):
        super(ChatReadMessageView, self).create(request, *args, **kwargs)
        return Response(status=status.HTTP_200_OK)


class ChatTotalUnreadMessageCountView(views.APIView):
    """Total unread messages across ALL rooms for the current user."""

    def get(self, request, *args, **kwargs):
        user = self.request.user
        return Response(
            {
                "count": models.ChatMessage.objects.exclude(sender=user)
                .exclude(room__participants__blacklist_owner__foe=user)
                .exclude(room__participants__blacked_user__owner=user)
                .filter(room__participants=user)
                .filter(~Q(chatreadmessage__user=user))
                .count()
            }
        )


class ChatRoomMessageCountView(views.APIView):
    """Total message count in one room (for the pagination UI)."""

    permission_classes = (permissions.ChatMessagePermission,)

    def get(self, request, *args, **kwargs):
        count = models.ChatMessage.objects.filter(
            room_id=self.kwargs.get("pk")
        ).count()
        return Response({"count": count})


class ChatRoomUnreadMessageCountView(views.APIView):
    """Unread message count in ONE room for the current user."""

    permission_classes = (permissions.ChatMessagePermission,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        count = (
            models.ChatMessage.objects.filter(room_id=self.kwargs.get("pk"))
            .exclude(sender=user)
            .filter(~Q(chatreadmessage__user=user))
            .count()
        )
        return Response({"count": count})


class ChatRoomDetailView(generics.RetrieveAPIView):
    """MessageList view"""

    serializer_class = serializers.ChatRoomDetailSerializer
    permission_classes = (permissions.ChatMessagePermission,)
    queryset = models.ChatRoom.objects.all()


class ChatRoomListView(generics.ListAPIView):
    """Chat room list view"""

    serializer_class = serializers.ChatRoomListSerializer
    filter_class = filters.ChatRoomListFilterSet
    pagination_class = ChatCursorPagination

    def get_queryset(self):
        """Override get queryset method"""
        user = self.request.user
        return (
            models.ChatRoom.objects.by_participant(participant=user)
            .annotate_last_message_datetime()
            .annotate_unread_messages(user)
            .annotate_message_count()
            .filter(message_count__gte=1)
        )


class ChatView(generics.GenericAPIView):
    """Private room view"""

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        """Override get method."""

        return render(
            request,
            "chat/private.html",
            {
                "rooms": models.ChatRoom.objects.by_participant(
                    participant=self.request.user
                )
            },
        )


class PrivateChatRoomCreateView(generics.CreateAPIView):
    """Create chat room"""

    serializer_class = serializers.PrivateChatRoomCreateSerializer
