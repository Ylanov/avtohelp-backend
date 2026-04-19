"""Version 1.0.0 url conf."""
from django.urls import path
from .views import (
    ChatMessageListView,
    ChatReadMessageView,
    ChatRoomDetailView,
    ChatRoomListView,
    ChatRoomMessageCountView,
    ChatRoomUnreadMessageCountView,
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
    # MORE SPECIFIC routes first — "/count" and "/unread/count" must match
    # before the generic "/<pk>" list view.
    path(
        "messages/room/<int:pk>/count",
        ChatRoomMessageCountView.as_view(),
        name="message-room-count",
    ),
    path(
        "messages/room/<int:pk>/unread/count",
        ChatRoomUnreadMessageCountView.as_view(),
        name="message-room-unread-count",
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
