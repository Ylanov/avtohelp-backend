from rest_framework import serializers
from chat import models
from account.models import User
from userprofile import models as profile_models
from utils import api_exceptions


class ChatRoomParticipantsSerializer(serializers.ModelSerializer):
    """Serializer for field participants in ChatRoom """

    id = serializers.IntegerField(source='profile.id')
    first_name = serializers.CharField(source='get_first_name')
    last_name = serializers.CharField(source='get_last_name')
    middle_name = serializers.CharField(source='get_middle_name')
    avatar = serializers.ImageField(source='profile.image')

    class Meta:
        """Meta class"""
        model = User
        fields = ('id', 'first_name', 'last_name', 'middle_name', 'avatar')


class ChatMessageListSerializer(serializers.ModelSerializer):
    """Serializer for model Message"""

    sender = ChatRoomParticipantsSerializer()
    read = serializers.BooleanField()

    class Meta:
        """Meta class"""
        model = models.ChatMessage
        fields = ('id', 'created', 'modified',
                  'sender', 'room', 'message', 'read')


class ChatRoomDetailSerializer(serializers.ModelSerializer):
    """Serializer for model Message"""

    participants = ChatRoomParticipantsSerializer(many=True)

    class Meta:
        """Meta class"""
        model = models.ChatRoom
        fields = ('id', 'created', 'modified',
                  'participants', 'name', 'is_public')


class ChatRoomListSerializer(serializers.ModelSerializer):
    """Serializer for model ChatRoom"""

    participants = ChatRoomParticipantsSerializer(many=True)
    avatar = serializers.ImageField(source='image')

    class Meta:
        """Meta class"""
        model = models.ChatRoom
        fields = ('id', 'created', 'participants', 'avatar', 'is_public')


class PrivateChatRoomCreateSerializer(serializers.ModelSerializer):
    """Serializer for create ChatRoom"""

    # REQUEST
    participant = serializers.PrimaryKeyRelatedField(queryset=profile_models.Profile.objects.select_related('user').all(),
                                                     write_only=True)

    # RESPONSE
    participants = ChatRoomParticipantsSerializer(read_only=True,
                                                  required=False,
                                                  many=True)
    is_public = serializers.BooleanField(read_only=True)

    class Meta:
        """Meta class"""
        model = models.ChatRoom
        fields = ('id', 'created', 'participant', 'participants', 'is_public')

    def validate(self, attrs):
        """Override validate method"""
        attrs['initiator'] = self.context.get('request').user
        attrs['participant'] = attrs.get('participant').user

        # Check if participant is not an initiator
        if attrs['initiator'] == attrs['participant']:
            raise api_exceptions.EqualIDError()

        # Check if participant not in black list
        are_foes = profile_models.BlackList.objects.are_foes(attrs['initiator'], attrs['participant'])
        if are_foes:
            raise api_exceptions.AreFoesError(attrs['initiator'], attrs['participant'])

        # Check if chat room is already exists
        room = models.ChatRoom.objects.private(attrs['initiator'], attrs['participant'])
        if room.exists():
            raise api_exceptions.ChatRoomAlreadyExistsError(attrs['initiator'], attrs['participant'])

        return attrs

    def create(self, validated_data):
        """Override create method"""
        obj = models.ChatRoom.objects.make(participants=validated_data.values(), public=False)
        return obj
