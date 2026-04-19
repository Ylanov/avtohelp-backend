from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

from chat import consumers
from chat.token_auth import TokenAuthMiddleware

# Channels 4 requires http to be explicitly wired to Django's ASGI app,
# otherwise all HTTP requests would fall through to the default 404.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": TokenAuthMiddleware(
            URLRouter(
                [
                    path("chat/stream", consumers.ChatConsumer.as_asgi()),
                ]
            ),
        ),
    }
)
