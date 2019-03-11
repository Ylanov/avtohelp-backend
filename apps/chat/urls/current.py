"""Version 1.0.0 url conf."""
from django.urls import path

from chat.views import current as views
from chat import consumers


app_name = 'chat'

# urlpatterns = [
#     path('messages/<int:sender>/<int:receiver>', views.MessageListView.as_view(), name='message-list'),  # For GET request.
#     path('message/create', views.MessageCreateView.as_view(), name='message-create'),  # For GET request.
#     path('', views.index, name='index'),
#     path('<int:room_name>', views.room, name='room')
#
# ]

from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<room_name>[^/]+)/$', views.room, name='room'),
]
