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
        #  Decode binary strings and pack it to dictionary
        headers = dict()
        for tuple_obj in scope["headers"]:
            key, value = (
                tuple_obj[0]
                if not hasattr(tuple_obj[0], "decode")
                else tuple_obj[0].decode(),
                tuple_obj[1]
                if not hasattr(tuple_obj[1], "decode")
                else tuple_obj[1].decode(),
            )
            headers[key] = value

        try:
            if "authorization" in headers:
                token_name, token_key = headers["authorization"].split()
                token = Token.objects.get(key=token_key)
                scope["user"] = token.user
            else:
                # todo: uses for chat in web view
                cookie = {
                    i.split("=")[0].lstrip(): i.split("=")[1]
                    for i in headers.get("cookie").split(";")
                }
                session = Session.objects.get(session_key=cookie.get("sessionid"))
                session_data = session.get_decoded()
                scope["user"] = User.objects.get(id=session_data.get("_auth_user_id"))
        except:
            scope["user"] = AnonymousUser()
        return self.inner(scope)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))
