from rest_framework import generics, views, status
from rest_framework.exceptions import NotAuthenticated

from account import models as account_models
from authorization import models as models
from authorization.serializers import current as serializers


class AuthorizationView(generics.CreateAPIView):
    """
    View for get or create user.
    Request: {"phone": "+79000000000"}
    Response: {"id": 1, "phone": "+79000000000"}
    :return: object
    """

    serializer_class = serializers.AuthorizationSerializer
    queryset = account_models.User.objects.all()


class PhoneVerificationView(generics.CreateAPIView):
    """
    View for verify user phone number
    Request: {"phone": "+79000000000"}
    Response: {"detail": ""Sms was sent}
    :return: object
    """

    serializer_class = serializers.PhoneVerificationSerializer
    queryset = models.SMSCode.objects.all()


class AuthenticationView(generics.CreateAPIView):
    """
    View for verify user phone
    Request: {"phone": "+79000000000", "sms_code": "1234"}
    Response: {"token": "fsioufuy49fu490f9wehfofhiodhfio"}
    :return: object
    """

    serializer_class = serializers.AuthenticationSerializer
    queryset = account_models.User.objects.all()


class LogoutView(views.APIView):
        """
        An endpoint for logout.
        Logout authorized user by recreating token (delete existed token and create a new one)
        :return: None
        """

        queryset = account_models.User.objects.all()

        def post(self, request, format=None):
            """Delete existed auth token and then create new one for logout"""
            if not request.user.is_anonymous:
                request.user.regenerate_auth_token()
                return views.Response(status=status.HTTP_200_OK)
            else:
                raise NotAuthenticated()
