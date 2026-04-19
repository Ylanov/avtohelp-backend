"""
ASGI entry point for Daphne (WebSocket + HTTP).

Channels 4 prefers an explicit import of the ProtocolTypeRouter instance
rather than the old get_default_application() that relied on
ASGI_APPLICATION setting lookup at runtime.
"""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roadhelpbackend.settings.prod")
django.setup()

# Must import after django.setup() — the router touches apps / models.
from .routing import application  # noqa: E402

__all__ = ["application"]
