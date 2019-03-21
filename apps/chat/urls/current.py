"""Version 1.0.0 url conf."""
from django.urls import path

from chat.views import current as views

app_name = 'chat'

urlpatterns = [
    path('', views.ChatRoomListView.as_view(), name='room-list'),
    path('messages/room/<int:room>', views.ChatMessageListView.as_view(), name='message-list'),
    path('<int:room>', views.ChatRoomPrivateView.as_view(), name='room-join'),
    path('private/create', views.PrivateChatRoomCreateView.as_view(), name='private-room-create')
]
