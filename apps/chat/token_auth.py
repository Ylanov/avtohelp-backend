from channels.auth import AuthMiddlewareStack, SessionMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from rest_framework.authtoken.models import Token

from account.models import User


class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        headers = dict(scope['headers'])
        try:
            if b'authorization' in headers:
                token_name, token_key = headers[b'authorization'].decode().split()
                token = Token.objects.get(key=token_key)
                scope['user'] = token.user
            else:
                cookie = {i.split('=')[0].strip(): i.split('=')[1].strip()
                          for i in headers.get(b'cookie').decode().split(';')}
                session = Session.objects.get(session_key=cookie.get('sessionid'))
                session_data = session.get_decoded()
                scope['user'] = User.objects.get(id=session_data.get('_auth_user_id'))
        except:
            scope['user'] = AnonymousUser()
        return self.inner(scope)

TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))
