from channels.auth import AuthMiddlewareStack
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
        if b'authorization' in headers:
            try:
                token_name, token_key = headers[b'authorization'].decode().split()
                if token_name == 'Token':
                    token = Token.objects.get(key=token_key)
                    scope['user'] = token.user
            except Token.DoesNotExist:
                scope['user'] = AnonymousUser()
        else:
            try:
                session = Session.objects.get(session_key=headers.get(b'cookie').decode().split()[1].split('=')[1])
                session_data = session.get_decoded()
                scope['user'] = User.objects.get(id=session_data.get('_auth_user_id'))
            except:
                scope['user'] = AnonymousUser()
        return self.inner(scope)

TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))
