from rest_framework import serializers, response

from account.models import User
from chat import models
from userprofile import models as profile_models
from utils import api_exceptions


class ChatRoomParticipantsSerializer(serializers.ModelSerializer):
    """Serializer for field participants in ChatRoom """

    id = serializers.IntegerField(source='profile.id')
    first_name = serializers.CharField(source='get_first_name')
    last_name = serializers.CharField(source='get_last_name')
    avatar = serializers.ImageField(source='profile.image')

    class Meta:
        """Meta class"""
        model = User
        fields = ('id', 'first_name', 'last_name', 'avatar')


class ChatMessageListSerializer(serializers.ModelSerializer):
    """Serializer for model Message"""

    sender = ChatRoomParticipantsSerializer()
    read = serializers.BooleanField()

    class Meta:
        """Meta class"""
        model = models.ChatMessage
        fields = ('id', 'created', 'modified',
                  'sender', 'room_id', 'message', 'read')


class ChatReadMessageSerializer(serializers.ModelSerializer):
    """Serializer for model ChatReadMessage"""

    # REQUEST
    messages = serializers.PrimaryKeyRelatedField(
        queryset=models.ChatMessage.objects.all(),
        many=True,
        write_only=True,
        allow_null=False,
        allow_empty=False
    )

    class Meta:
        """Meta class"""
        model = models.ChatReadMessage
        fields = ('messages',)

    def validate(self, attrs):
        """Validate method"""
        user = self.context.get('request').user
        messages = attrs.get('messages')

        # Check existence of requested messages
        qs = models.ChatMessage.objects.exclude(sender=user)\
                                       .exclude(chatreadmessage__user_id=user)\
                                       .filter(id__in=[message.id for message in messages])
        attrs['messages'] = list(qs)
        return attrs

    def create(self, validated_data):
        for message in validated_data.get('messages'):
            if message is not None:
                self.Meta.model.objects.bulk_create([
                    self.Meta.model(user=self.context.get('request').user,
                                    message=message)
                ])
        return response.Response()


class ChatRoomDetailSerializer(serializers.ModelSerializer):
    """Serializer for model Message"""

    participants = ChatRoomParticipantsSerializer(many=True)

    class Meta:
        """Meta class"""
        model = models.ChatRoom
        fields = ('id', 'created', 'modified',
                  'participants', 'name', 'image')


class LastChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for last message from chat"""

    class Meta:
        """Meta class"""
        model = models.ChatMessage
        fields = ('id', 'created', 'message')


class ChatRoomListSerializer(serializers.ModelSerializer):
    """Serializer for model ChatRoom"""

    participants = ChatRoomParticipantsSerializer(many=True)
    last_message = LastChatMessageSerializer(source='chatmessage_set.first')
    unread_messages = serializers.IntegerField(read_only=True)
    message_count = serializers.IntegerField(read_only=True)

    class Meta:
        """Meta class"""
        model = models.ChatRoom
        fields = ('id', 'created', 'participants',
                  'image', 'name', 'last_message',
                  'unread_messages', 'message_count')


class PrivateChatRoomCreateSerializer(serializers.ModelSerializer):
    """Serializer for create ChatRoom"""

    # REQUEST
    participant = serializers.PrimaryKeyRelatedField(queryset=profile_models.Profile.objects.select_related('user').all(),
                                                     write_only=True)

    # RESPONSE
    participants = ChatRoomParticipantsSerializer(read_only=True,
                                                  required=False,
                                                  many=True)

    class Meta:
        """Meta class"""
        model = models.ChatRoom
        fields = ('id', 'created', 'participant', 'participants')

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
