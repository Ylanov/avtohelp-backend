"""Version 1.0.0 url conf."""
from django.urls import path
from views import (
    ChatMessageListView,
    ChatReadMessageView,
    ChatRoomDetailView,
    ChatRoomListView,
    ChatTotalUnreadMessageCountView,
    ChatView,
    PrivateChatRoomCreateView,
)

app_name = "chat"

urlpatterns = [
    path("rooms", ChatRoomListView.as_view(), name="room-list"),
    path(
        "rooms/<int:pk>",
        ChatRoomDetailView.as_view(),
        name="room-detail",
    ),
    path(
        "rooms/private/create",
        PrivateChatRoomCreateView.as_view(),
        name="private-room-create",
    ),
    path(
        "messages/room/<int:pk>",
        ChatMessageListView.as_view(),
        name="message-list",
    ),
    path(
        "messages/unread/count",
        ChatTotalUnreadMessageCountView.as_view(),
        name="message-total-unread-count",
    ),
    path(
        "messages/<int:pk>/read",
        ChatReadMessageView.as_view(),
        name="message-read",
    ),
    # Test use
    path("stream", ChatView.as_view(), name="chat"),
]
