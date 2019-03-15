from rest_framework import serializers
from chat import models
from account.models import User
from userprofile import models as profile_models
from utils import api_exceptions


class MessageListSerializer(serializers.ModelSerializer):
    """Serializer for model Message"""

    class Meta:
        """Meta class"""
        model = models.ChatMessage
        fields = ('id', 'created', 'modified', 'is_read', 'message')


class ChatRoomListSerializer(serializers.ModelSerializer):
    """Serializer for model ChatRoom"""

    class Meta:
        """Meta class"""
        model = models.ChatRoom
        fields = ('id', 'created', 'initiator',
                  'participant', 'is_public')


class ChatProfileDetailSerializer(serializers.ModelSerializer):
    """Serializer for chat participants"""

    class Meta:
        """Meta class"""
        model = profile_models.Profile
        fields = ('id', 'first_name', 'last_name', 'avatar')


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating message """

    # RESPONSE
    sender = ChatProfileDetailSerializer(source='sender.profile', read_only=True)
    receiver = ChatProfileDetailSerializer(source='receiver.profile', read_only=True)

    # REQUEST
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_active=True))
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_active=True))

    # COMMON
    message = serializers.CharField()

    class Meta:
        """Meta class"""
        model = models.ChatMessage
        fields = ('id', 'created', 'modified', 'message',
                  'is_read', 'sender', 'receiver')

    def validate(self, attrs):
        """Override validated method"""
        if attrs['sender'].id == attrs['receiver'].id:
            raise api_exceptions.EqualIDError()
        return attrs
