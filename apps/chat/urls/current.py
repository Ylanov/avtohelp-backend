"""Version 1.0.0 url conf."""
from django.urls import path

from chat.views import current as views

app_name = 'chat'

urlpatterns = [
    path('messages/<int:sender>/<int:receiver>', views.MessageListView.as_view(), name='message-list'),  # For GET request.
    path('message/create', views.MessageCreateView.as_view(), name='message-create'),  # For GET request.
]