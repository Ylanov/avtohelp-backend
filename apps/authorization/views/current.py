from rest_framework import generics, views, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from account import models as account_models
from authorization import models as models
from authorization.serializers import current as serializers


class PhoneVerificationView(generics.CreateAPIView):
    """
    View for verify user phone number
    Request: {"phone": "+79000000000", "city": 1}
    Response: {"detail": ""Sms was sent}
    :return: object
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.PhoneVerificationSerializer
    queryset = models.SMSCode.objects.all()


class AuthorizationView(generics.CreateAPIView):
    """
    View for verify user phone
    Request: {"phone": "+79000000000", "code": "1234"}
    Response: {"token": "fsioufuy49fu490f9wehfofhiodhfio"}
    :return: object
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.AuthorizationView
    queryset = models.SMSCode.objects.all()


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

