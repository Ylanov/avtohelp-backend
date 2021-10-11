from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from account.models import User
from chat.models import ChatRoom, ChatMessage, ChatReadMessage
from userprofile.models import BlackList, FriendList, FriendRequest
from utils import api_exceptions


class TestChat(APITestCase):
    VERSION = settings.AVAILABLE_VERSIONS.get("current")

    @classmethod
    def setUpClass(cls):
        """Set up for class"""
        print(f"\nStart test chat app v{cls.VERSION}")
        print("==========")

    @classmethod
    def tearDownClass(cls):
        """Tear down for class"""
        print("==========")
        print(f"End test chat app v{cls.VERSION}\n")

    def setUp(self):
        # Create users
        self.user = User.objects.make(phone="+79000000000")
        self.user_1 = User.objects.make(phone="+79000000001")
        self.user_2 = User.objects.make(phone="+79000000002")
        self.user_3 = User.objects.make(phone="+79000000003")
        self.user_4 = User.objects.make(phone="+79000000004")
        self.user_5 = User.objects.make(phone="+79000000005")

        # Add user_1 to friend list
        friend_request = FriendRequest.objects.create(
            owner=self.user, invited=self.user_1, approved=True
        )
        FriendList.objects.create(
            owner=self.user, friend=self.user_1, request=friend_request
        )
        # Add user_5 to friend list
        friend_request = FriendRequest.objects.create(
            owner=self.user, invited=self.user_5, approved=True
        )
        FriendList.objects.create(
            owner=self.user, friend=self.user_5, request=friend_request
        )

        # Add user_2 to black list
        BlackList.objects.create(owner=self.user, foe=self.user_2)
        BlackList.objects.create(owner=self.user, foe=self.user_3)
        BlackList.objects.create(owner=self.user, foe=self.user_5)

        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_room_list(self):
        """Test view for getting list of chats"""
        # Create Chat Room
        ChatRoom.objects.make(participants=[self.user, self.user_1], public=False)
        ChatRoom.objects.make(participants=[self.user, self.user_2], public=False)
        ChatRoom.objects.make(participants=[self.user_1, self.user_2], public=False)
        ChatRoom.objects.make(participants=[self.user_1, self.user_3], public=False)

        api_path = "%s:chat:room-list" % settings.AVAILABLE_VERSIONS.get("current")
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data.get("results")),
            ChatRoom.objects.by_participant(self.user).count(),
        )

    def test_room_detail(self):
        """Test view for getting detail info about room"""
        # Create Chat Room
        room = ChatRoom.objects.make(
            participants=[self.user, self.user_1], public=False
        )
        ChatRoom.objects.make(participants=[self.user, self.user_2], public=False)
        ChatRoom.objects.make(participants=[self.user_1, self.user_2], public=False)
        ChatRoom.objects.make(participants=[self.user_1, self.user_3], public=False)

        api_path = "%s:chat:room-detail" % settings.AVAILABLE_VERSIONS.get("current")
        response = self.client.get(reverse(api_path, kwargs={"pk": room.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("id"), room.id)

    def test_room_detail_1(self):
        """Test view for getting detail info about room"""
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_2)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        # Create Chat Room
        room = ChatRoom.objects.make(
            participants=[self.user, self.user_1], public=False
        )
        ChatRoom.objects.make(participants=[self.user, self.user_2], public=False)
        ChatRoom.objects.make(participants=[self.user_1, self.user_2], public=False)
        ChatRoom.objects.make(participants=[self.user_1, self.user_3], public=False)

        api_path = "%s:chat:room-detail" % settings.AVAILABLE_VERSIONS.get("current")
        response = self.client.get(reverse(api_path, kwargs={"pk": room.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_chat_messages_list(self):
        """Test view for messages of chat room"""
        # Create Chat Room
        room = ChatRoom.objects.make(
            participants=[self.user, self.user_1], public=False
        )

        # Create messages
        ChatMessage.objects.create(sender=self.user, room=room, message="Hi")
        ChatMessage.objects.create(sender=self.user_1, room=room, message="Hello")

        api_path = "%s:chat:message-list" % settings.AVAILABLE_VERSIONS.get("current")
        response = self.client.get(reverse(api_path, kwargs={"pk": room.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(len(response.data.get("results")))

    def test_chat_messages_list_1(self):
        """Test view for messages of chat room"""
        # Authorize user_3, that not allowed to read this conversation
        self.token, created = Token.objects.get_or_create(user=self.user_3)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        # Create Chat Room
        room = ChatRoom.objects.make(
            participants=[self.user, self.user_1], public=False
        )

        # Create messages
        ChatMessage.objects.create(sender=self.user, room=room, message="Hi")
        ChatMessage.objects.create(sender=self.user_1, room=room, message="Hello")

        api_path = "%s:chat:message-list" % settings.AVAILABLE_VERSIONS.get("current")
        response = self.client.get(reverse(api_path, kwargs={"pk": room.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_total_chat_room_messages_unread_count(self):
        """
        Test total count of unread messages in rooms
        Participants: user_1, user_2
        Mechanism: from user_1 to user_2 (m_1), from user_2 to user_1 (m_2),
                   from user_2 to user_1 (m_3)
        Messages: m_1, m_2, m_3
        """
        # Authorize user_3, that not allowed to read this conversation
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        # Create Chat Room
        room = ChatRoom.objects.make(
            participants=[self.user_1, self.user_2], public=False
        )

        # Create messages
        m_1 = ChatMessage.objects.create(sender=self.user_1, room=room, message="Hi")
        m_2 = ChatMessage.objects.create(sender=self.user_2, room=room, message="Hello")
        m_3 = ChatMessage.objects.create(
            sender=self.user_2, room=room, message="How u doing"
        )

        # check counter without readings
        api_path = (
            "%s:chat:message-total-unread-count"
            % settings.AVAILABLE_VERSIONS.get("current")
        )
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 2)

        # check with readings
        # emulate read message
        ChatReadMessage.objects.create(user=self.user_1, message=m_2)
        api_path = (
            "%s:chat:message-total-unread-count"
            % settings.AVAILABLE_VERSIONS.get("current")
        )
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 1)

    def test_total_count_chat_room_unread_messages_w_blacklisted_user(self):
        """
        Test total count of unread chat room messages with blacklisted user
        Participants: user_1, user_2
        Blacklist: BlackList_obj (owner: user_1, foe: user_2)
        Total messages: 3 (user_1 to user_2, user_2 to user_1, user_2 to user_1)
        Total messages exclude message from blacklisted user: 1
        Mechanism: user_1 write message to user_2 (M1), user_2 answered user_1 (M2),
                   *user_1 blacklisted user_2*, user_2 try to reply user_1 (M3)

        Correct count before block: 1
        Correct count after block, without readings: 0
        """
        # Authorize user_1, that not allowed to read this conversation
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        # Create Chat Room
        room = ChatRoom.objects.make(
            participants=[self.user_1, self.user_2], public=False
        )

        # Create messages and check count
        m_1 = ChatMessage.objects.create(sender=self.user_1, room=room, message="Hi")

        m_2 = ChatMessage.objects.create(sender=self.user_2, room=room, message="Hello")
        api_path = (
            "%s:chat:message-total-unread-count"
            % settings.AVAILABLE_VERSIONS.get("current")
        )
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 1)

        # user_1 read user_2 message
        ChatReadMessage.objects.create(user=self.user_1, message=m_2)
        api_path = (
            "%s:chat:message-total-unread-count"
            % settings.AVAILABLE_VERSIONS.get("current")
        )
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 0)

        # user_1 add user_2 to blacklist
        bl = BlackList.objects.create(owner=self.user_1, foe=self.user_2)

        # blacklisted user_2 try to sent message to user_1
        m_3 = ChatMessage.objects.create(
            sender=self.user_2, room=room, message="Hey what's up??"
        )

        # check unread messages for user_1
        api_path = (
            "%s:chat:message-total-unread-count"
            % settings.AVAILABLE_VERSIONS.get("current")
        )
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 0)

        # check unread messages if we remove user_2 from blacklist user_1
        bl.delete()

        api_path = (
            "%s:chat:message-total-unread-count"
            % settings.AVAILABLE_VERSIONS.get("current")
        )
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 1)

    def test_room_create(self):
        """Test create chat room"""
        api_path = "%s:chat:private-room-create" % settings.AVAILABLE_VERSIONS.get(
            "current"
        )
        response = self.client.post(
            reverse(api_path), data={"participant": self.user_1.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_chat_create_error_2(self):
        """Test create chat room w/ person who is in your black list"""
        api_path = "%s:chat:private-room-create" % settings.AVAILABLE_VERSIONS.get(
            "current"
        )
        response = self.client.post(
            reverse(api_path), data={"participant": self.user_3.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("status_code"),
            api_exceptions.AreFoesError.extended_status_code,
        )

    def test_chat_create_error_3(self):
        """Test create chat room w/ person who was your friend but now in black list"""
        api_path = "%s:chat:private-room-create" % settings.AVAILABLE_VERSIONS.get(
            "current"
        )
        response = self.client.post(
            reverse(api_path), data={"participant": self.user_5.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("status_code"),
            api_exceptions.AreFoesError.extended_status_code,
        )

    def test_chat_create_error_4(self):
        """Test create chat room w/ myself"""
        api_path = "%s:chat:private-room-create" % settings.AVAILABLE_VERSIONS.get(
            "current"
        )
        response = self.client.post(
            reverse(api_path), data={"participant": self.user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("status_code"),
            api_exceptions.EqualIDError.extended_status_code,
        )

    def test_impossibility_chatting_with_blacklisted_user(self):
        """
        Test impossibility chatting with blacklisted user
        Participants: user, user_1
        ChatRoom: Room_1 (user, user_1)
        user backlisted user_1
        Now chat room list should return not a single room 'cause of Blacklist obj

        """
        # Authorize user_3, that not allowed to read this conversation
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        # Create Chat Room
        ChatRoom.objects.make(participants=[self.user, self.user_1], public=False)

        # Added to blacklist
        BlackList.objects.create(owner=self.user, foe=self.user_1)

        api_path = "%s:chat:room-list" % settings.AVAILABLE_VERSIONS.get("current")
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 0)

    def test_possibility_chatting_only_with_friends(self):
        """
        Test possibility chatting only with friends
        Participants: user, user_1
        ChatRoom: Room_1 (user, user_1)
        user add to friend user_1
        Now chat room list should return only rooms when participants are friends

        """
        # Authorize user_3, that not allowed to read this conversation
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        # Create Chat Room
        chat_room = ChatRoom.objects.make(
            participants=[self.user, self.user_1], public=False
        )

        self.assertEqual(chat_room, ChatRoom.objects.friends(self.user_1).first())
        self.assertEqual(ChatRoom.objects.friends(self.user_1).count(), 1)

    def test_chat_room_unread_messages_counter(self):
        """
        Test counter of unread messages
        Participants: user_1, user_2
        Mechanism: user_1 wrote message to user_2 (m_1), user_2 wrote twice to user_1 (m_2 & m_3)
        Correct count of unread messages: 2 (as user_1), 1 (as user_2)
        """

        # Authorize user_1, that not allowed to read this conversation
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        # Create Chat Room
        room = ChatRoom.objects.make(
            participants=[self.user_1, self.user_2], public=False
        )

        # Create messages and check count
        m_1 = ChatMessage.objects.create(sender=self.user_1, room=room, message="Hi")

        m_2 = ChatMessage.objects.create(sender=self.user_2, room=room, message="Hello")
        m_3 = ChatMessage.objects.create(
            sender=self.user_2, room=room, message="Y ur silent?"
        )

        api_path = "%s:chat:room-list" % settings.AVAILABLE_VERSIONS.get("current")
        response = self.client.get(reverse(api_path), kwargs={"pk": room.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("results")[0].get("unread_messages"), 2)

        # Authorize user_1, that not allowed to read this conversation
        self.token, created = Token.objects.get_or_create(user=self.user_2)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        api_path = "%s:chat:room-list" % settings.AVAILABLE_VERSIONS.get("current")
        response = self.client.get(reverse(api_path), kwargs={"pk": room.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("results")[0].get("unread_messages"), 1)

    def test_chat_messages_annotated_read_status(self):
        """
        Test chat messages annotated read status
        Participants: user_1, user_2
        Mechanism: user_1 sent user_2 message (m_1), user_2 reply user_1 twice (m_2, m_3)
        """
        # Authorize user_1, that not allowed to read this conversation
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        # Create chat room
        room = ChatRoom.objects.make(
            participants=[self.user, self.user_1], public=False
        )

        # Create messages
        m_1 = ChatMessage.objects.create(sender=self.user_1, room=room, message="Hi")
        m_2 = ChatMessage.objects.create(sender=self.user_2, room=room, message="Hello")
        m_3 = ChatMessage.objects.create(sender=self.user_2, room=room, message="sup")

        api_path = "%s:chat:message-list" % settings.AVAILABLE_VERSIONS.get("current")
        response = self.client.get(reverse(api_path, kwargs={"pk": room.id}))
        for message in response.data.get("results"):
            if message.get("sender").get("id") != self.user_1.id:
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(message.get("read"), False)
            else:
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(message.get("read"), True)

        # Emulate messages reading
        ChatReadMessage.objects.create(user=self.user_1, message=m_2)
        ChatReadMessage.objects.create(user=self.user_1, message=m_3)
        api_path = "%s:chat:message-list" % settings.AVAILABLE_VERSIONS.get("current")
        response = self.client.get(reverse(api_path, kwargs={"pk": room.id}))
        for message in response.data.get("results"):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(message.get("read"), True)

    def test_chat_room_list_filter_by_participant_id(self):
        """Test retrieving chat rooms filtered by participant_id"""
        # Create Chat Room
        room_1 = ChatRoom.objects.make(
            participants=[self.user, self.user_1], public=False
        )
        room_2 = ChatRoom.objects.make(
            participants=[self.user, self.user_2], public=False
        )
        room_3 = ChatRoom.objects.make(
            participants=[self.user_1, self.user_2], public=False
        )
        room_4 = ChatRoom.objects.make(
            participants=[self.user_1, self.user_3], public=False
        )

        api_path = "%s:chat:room-list" % settings.AVAILABLE_VERSIONS.get("current")
        response = self.client.get(
            reverse(api_path), data={"participant_id": self.user_1.profile.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data.get("results")),
            ChatRoom.objects.by_participant(self.user)
            .filter(participants=self.user_1.profile.id)
            .count(),
        )
        self.assertEqual(response.data.get("results")[0].get("id"), room_1.id)

    def test_chat_room_list_filter_by_publicity(self):
        """
        Test retrieving chat rooms filtered by status - public
        """
        # Create Chat Room
        ChatRoom.objects.make(participants=[self.user, self.user_1], public=False)
        ChatRoom.objects.make(participants=[self.user, self.user_2], public=False)
        ChatRoom.objects.make(participants=[self.user_1, self.user_2], public=False)
        ChatRoom.objects.make(participants=[self.user_1, self.user_3], public=False)

        api_path = "%s:chat:room-list" % settings.AVAILABLE_VERSIONS.get("current")
        response = self.client.get(reverse(api_path), data={"is_public": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data.get("results")),
            ChatRoom.objects.by_participant(self.user).public().count(),
        )

    def test_ordering_chat_rooms_by_last_message(self):
        """
        Test retrieving chat rooms ordered by last message
        """

        # Create Chat Room
        room_1 = ChatRoom.objects.make(
            participants=[self.user, self.user_1], public=False
        )
        room_2 = ChatRoom.objects.make(
            participants=[self.user, self.user_4], public=False
        )

        # Create chat message in room 1
        ChatMessage.objects.create(sender=self.user_1, room=room_1, message="Message")

        api_path = "%s:chat:room-list" % settings.AVAILABLE_VERSIONS.get("current")
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("results")[0].get("id"), room_1.id)
