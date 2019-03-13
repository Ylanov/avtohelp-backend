from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from chat import consumers

import chat.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter([
            url(r'^ws/chat/(?P<recipient>[^/]+)$', consumers.ChatConsumer, name='room')
            # chat.routing.websocket_urlpatterns
        ])
    ),
})
