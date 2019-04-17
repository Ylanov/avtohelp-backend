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
        #  Decode binary strings and pack to dictionary
        headers = {i[0].decode(): i[1].decode() for i in scope['headers']}
        try:
            if 'authorization' in headers:
                token_name, token_key = headers['authorization'].split()
                token = Token.objects.get(key=token_key)
                scope['user'] = token.user
            else:
                cookie = {i.split('=')[0].lstrip(): i.split('=')[1] for i in headers.get('cookie').split(';')}
                session = Session.objects.get(session_key=cookie.get('sessionid'))
                session_data = session.get_decoded()
                scope['user'] = User.objects.get(id=session_data.get('_auth_user_id'))
        except:
            scope['user'] = AnonymousUser()
        return self.inner(scope)

TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))
