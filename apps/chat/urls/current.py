"""Version 1.0.0 url conf."""
from django.urls import path

from chat.views import current as views

app_name = 'chat'

urlpatterns = [
    path('', views.ChatRoomListView.as_view(), name='room-list'),
    path('messages/room/<int:pk>', views.ChatMessageListView.as_view(), name='message-list'),
    path('messages/room/<int:pk>/count', views.ChatMessageCountView.as_view(), name='message-count'),
    path('rooms/<int:pk>', views.ChatRoomPrivateView.as_view(), name='room-join'),
    path('rooms/<int:pk>/detail', views.ChatRoomDetailView.as_view(), name='room-detail'),
    path('private/create', views.PrivateChatRoomCreateView.as_view(), name='private-room-create')
]
