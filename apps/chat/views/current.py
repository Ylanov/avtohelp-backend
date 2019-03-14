from rest_framework import generics
from chat.serializers import current as serializers
from chat import models
from account.models import User
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from rest_framework.response import Response
from rest_framework import status
from userprofile import models as profile_models
from rest_framework.permissions import AllowAny
from django.db.models import Q
from rest_framework.exceptions import APIException


class MessageListView(generics.ListAPIView):
    """MessageList view"""

    serializer_class = serializers.MessageListSerializer

    def get_queryset(self):
        """Override get_queryset method"""
        sender = generics.get_object_or_404(User.objects.filter(is_active=True), pk=self.kwargs.get('sender'))
        receiver = generics.get_object_or_404(User.objects.filter(is_active=True), pk=self.kwargs.get('receiver'))
        return models.ChatMessage.objects.filter(sender=sender, receiver=receiver)


class MessageCreateView(generics.CreateAPIView):
    """Message create view"""

    serializer_class = serializers.MessageCreateSerializer
    queryset = models.ChatMessage.objects.all()


class RoomView(generics.GenericAPIView):
    """Room view"""

    def get(self, request, *args, **kwargs):
        """Override get method."""
        # return render(request, 'chat/room.html', {
        #     'recipient_json': mark_safe(json.dumps(kwargs.get('recipient'))),
        #     'recipient_id': kwargs.get('recipient')})
        friends = profile_models.FriendList.objects.are_friends(owner=request.user,
                                                                user=kwargs.get('recipient'))
        if friends:
            return render(request, 'chat/room.html', {
                'recipient': kwargs.get('recipient'),
                'token': request.user.auth_token
            })
        else:
            raise APIException('not friend')


class RoomList(generics.GenericAPIView):
    """
    Root page view. This is essentially a single-page app, if you ignore the
    login and admin parts.
    """

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        """Override get method."""
        # Get a list of rooms, ordered alphabetically
        rooms = models.ChatRoom.objects.order_by("id")

        # Render that in the index template
        return render(request, "chat/index.html", {
            "rooms": rooms,
        })



