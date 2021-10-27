from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from chat import consumers
from chat.token_auth import TokenAuthMiddleware

application = ProtocolTypeRouter(
    {
        "websocket": TokenAuthMiddleware(
            URLRouter(
                [
                    path("chat/stream", consumers.ChatConsumer),
                ]
            ),
        ),
    }
)
