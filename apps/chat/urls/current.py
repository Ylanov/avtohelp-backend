"""Version 1.0.0 url conf."""
from django.urls import path

from chat.views import current as views

app_name = 'chat'

urlpatterns = [
    path('rooms', views.ChatRoomListView.as_view(), name='room-list'),
    path('rooms/<int:pk>', views.ChatRoomDetailView.as_view(), name='room-detail'),
    path('rooms/private/create', views.PrivateChatRoomCreateView.as_view(), name='private-room-create'),
    path('messages/room/<int:pk>', views.ChatMessageListView.as_view(), name='message-list'),
    path('messages/unread/count', views.ChatTotalUnreadMessageCountView.as_view(), name='message-total-unread-count'),
    # Test use
    path('stream', views.ChatView.as_view(), name='chat'),
]
