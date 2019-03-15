from rest_framework import generics, views, status
from rest_framework.response import Response

from account import models as account_models
from authorization.serializers import current as serializers
from utils import views as view_mixins


class PhoneVerificationView(view_mixins.AuthorizationViewMixin, generics.CreateAPIView):
    """
    View for verify user phone number
    Request: {"phone": "+79000000000"}
    Response: {"detail": ""Sms was sent}
    :return: object
    """

    serializer_class = serializers.PhoneVerificationSerializer


class AuthorizationView(view_mixins.AuthorizationViewMixin, generics.CreateAPIView):
    """
    View for verify user phone
    Request: {"phone": "+79000000000", "code": "1234"}
    Response: {"token": "fsioufuy49fu490f9wehfofhiodhfio"}
    :return: object
    """

    serializer_class = serializers.AuthorizationView


class LogoutView(views.APIView):
        """
        An endpoint for logout.
        Logout authorized user by recreating token (delete existed token and create a new one)
        :return: None
        """

        queryset = account_models.User.objects.all()

        def post(self, request, format=None):
            """Delete existed auth token and then create new one for logout"""
            self.request.user.logout()
            return Response(status=status.HTTP_204_NO_CONTENT)

