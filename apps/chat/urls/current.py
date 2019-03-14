"""Version 1.0.0 url conf."""
from django.urls import path
from chat.views import current as views
from chat import consumers
from django.conf.urls import url


app_name = 'chat'

# urlpatterns = [
#     path('messages/<int:sender>/<int:receiver>', views.MessageListView.as_view(), name='message-list'),
#     path('message/create', views.MessageCreateView.as_view(), name='message-create'),  # For GET request.
#     path('', views.index, name='index'),
#     path('<int:room_name>', views.room, name='room')
#     path('<int:user_pk>', views.room, name='personal-chat-room'),
# ]


urlpatterns = [
    # url(r'^(?P<user_id>[^/]+)/$', views.room, name='room'),
    # path('<int:recipient>', views.RoomView.as_view(), name='room-view')
    path('<int:recipient>', views.RoomView.as_view(), name='room-view'),
    path('', views.RoomList.as_view(), name='room-list'),
]
