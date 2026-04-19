from django.conf import settings
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import (
    generics,
    status,
    views,
)
from rest_framework.response import Response

from account import models as account_models
from authorization.serializers import current as serializers
from utils import views as view_mixins


def _phone_key(group, request):
    """Rate-limit key: phone number from request body (falls back to IP)."""
    return str(request.data.get("phone") or request.META.get("REMOTE_ADDR", ""))


@method_decorator(
    ratelimit(
        key="ip",
        rate=settings.RATELIMIT_AUTH_PER_IP,
        method="POST",
        block=True,
    ),
    name="post",
)
@method_decorator(
    ratelimit(
        key=_phone_key,
        rate=settings.RATELIMIT_AUTH_PER_PHONE,
        method="POST",
        block=True,
    ),
    name="post",
)
class PhoneVerificationView(
    view_mixins.AuthorizationViewMixin, generics.CreateAPIView
):
    """
    Request SMS verification code.
    Request: {"phone": "+79000000000"}
    Response: {} on success. Code is never echoed back in the response.
    Rate-limited per IP and per phone (see settings.RATELIMIT_AUTH_*).
    """

    serializer_class = serializers.PhoneVerificationSerializer


@method_decorator(
    ratelimit(
        key="ip",
        rate=settings.RATELIMIT_AUTH_PER_IP,
        method="POST",
        block=True,
    ),
    name="post",
)
@method_decorator(
    ratelimit(
        key=_phone_key,
        rate=settings.RATELIMIT_AUTH_PER_PHONE,
        method="POST",
        block=True,
    ),
    name="post",
)
class AuthorizationView(
    view_mixins.AuthorizationViewMixin, generics.CreateAPIView
):
    """
    Verify SMS code and exchange for auth token.
    Request: {"phone": "+79000000000", "code": "12345"}
    Response: {"token": "...", "profile": {...}}
    Rate-limited per IP and per phone.
    """

    serializer_class = serializers.AuthorizationView


class LogoutView(views.APIView):
    """Logout the authenticated user by deleting their auth token."""

    queryset = account_models.User.objects.all()

    def post(self, request, format=None):
        self.request.user.logout()
        return Response(status=status.HTTP_204_NO_CONTENT)
