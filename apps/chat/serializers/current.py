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


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    """Serializer for create ChatRoom"""

    # REQUEST
    participant = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_active=True))

    class Meta:
        """Meta class"""
        model = models.ChatRoom
        fields = ('id', 'created', 'initiator', 'participant', 'is_public')

    def validate(self, attrs):
        """Override validate method"""
        attrs['initiator'] = self.context.get('request').user

        # Check if participant is not an initiator
        if attrs['initiator'] == attrs['participant']:
            raise api_exceptions.EqualIDError()

        # Check if participant is friend of mine
        friends = profile_models.FriendList.objects.are_friends(attrs['initiator'], attrs['participant'])
        if not friends:
            raise api_exceptions.ArentFriends(attrs['initiator'], attrs['participant'])

        # Check if chat room is already exists
        room = models.ChatRoom.objects.by_paticipants(attrs['initiator'], attrs['participant'])
        if room.exists():
            raise api_exceptions.ChatRoomAlreadyExists(attrs['initiator'], attrs['participant'])
        return attrs
    
    def create(self, validated_data):
        """Override create method"""
        # Private chat room
        validated_data['is_public'] = False
        return super().create(validated_data)
