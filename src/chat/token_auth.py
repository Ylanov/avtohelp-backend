"""
WebSocket Token authorisation middleware for Django Channels 4.

Parses the `Authorization: Token <key>` header from the connecting scope and
sets `scope["user"]` to the matching account.User (or AnonymousUser).
Falls back to Django session cookie (`sessionid`) for the web admin chat view.
"""
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from rest_framework.authtoken.models import Token

from account.models import User


def _headers_to_dict(raw_headers):
    out = {}
    for key, value in raw_headers:
        k = key.decode() if isinstance(key, (bytes, bytearray)) else key
        v = value.decode() if isinstance(value, (bytes, bytearray)) else value
        out[k.lower()] = v
    return out


@database_sync_to_async
def _user_from_token(token_key):
    try:
        return Token.objects.select_related("user").get(key=token_key).user
    except Token.DoesNotExist:
        return AnonymousUser()


@database_sync_to_async
def _user_from_session(session_key):
    try:
        session = Session.objects.get(session_key=session_key)
        uid = session.get_decoded().get("_auth_user_id")
        if uid:
            return User.objects.get(id=uid)
    except (Session.DoesNotExist, User.DoesNotExist):
        pass
    return AnonymousUser()


class TokenAuthMiddleware:
    """Channels 4 async middleware."""

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = _headers_to_dict(scope.get("headers", []))
        user = AnonymousUser()

        auth = headers.get("authorization", "")
        if auth.lower().startswith("token "):
            user = await _user_from_token(auth.split(None, 1)[1].strip())
        elif "cookie" in headers:
            cookie_map = {}
            for chunk in headers["cookie"].split(";"):
                if "=" in chunk:
                    k, v = chunk.strip().split("=", 1)
                    cookie_map[k] = v
            if sid := cookie_map.get("sessionid"):
                user = await _user_from_session(sid)

        scope["user"] = user
        return await self.inner(scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))
