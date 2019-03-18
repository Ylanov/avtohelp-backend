"""Version 1.0.0 url conf."""
from django.urls import path

from chat.views import current as views

app_name = 'chat'

urlpatterns = [
    path('', views.ChatRoomListView.as_view(), name='room-list'),
    path('<int:room>', views.ChatRoomPrivateView.as_view(), name='room-join'),
    path('create', views.ChatRoomCreateView.as_view(), name='room-create')
]
