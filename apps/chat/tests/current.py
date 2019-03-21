from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from account.models import User
from userprofile.models import BlackList, FriendList, FriendRequest
from chat.models import ChatRoom
from utils import api_exceptions


class TestChat(APITestCase):
    VERSION = settings.AVAILABLE_VERSIONS.get('current')

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
        self.user = User.objects.make(phone='+79000000000')
        self.user_1 = User.objects.make(phone='+79000000001')
        self.user_2 = User.objects.make(phone='+79000000002')
        self.user_3 = User.objects.make(phone='+79000000003')
        self.user_4 = User.objects.make(phone='+79000000004')
        self.user_5 = User.objects.make(phone='+79000000005')

        # Add user_1 to friend list
        friend_request = FriendRequest.objects.create(owner=self.user, invited=self.user_1, approved=True)
        FriendList.objects.create(owner=self.user, friend=self.user_1, request=friend_request)
        # Add user_5 to friend list
        friend_request = FriendRequest.objects.create(owner=self.user, invited=self.user_5, approved=True)
        FriendList.objects.create(owner=self.user, friend=self.user_5, request=friend_request)

        # Add user_2 to black list
        BlackList.objects.create(owner=self.user, foe=self.user_2)
        BlackList.objects.create(owner=self.user, foe=self.user_3)
        BlackList.objects.create(owner=self.user, foe=self.user_5)

        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_chat_list(self):
        """Test view for getting list of chats"""
        # Create Chat Room
        ChatRoom.objects.make(participants=[self.user, self.user_1], public=False)
        ChatRoom.objects.make(participants=[self.user, self.user_2], public=False)
        ChatRoom.objects.make(participants=[self.user_1, self.user_2], public=False)
        ChatRoom.objects.make(participants=[self.user_1, self.user_3], public=False)

        api_path = '%s:chat:room-list' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), ChatRoom.objects.by_participant(self.user).count())

    def test_chat_create(self):
        """Test create chat room"""
        api_path = '%s:chat:private-room-create' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.post(reverse(api_path), data={'participant': self.user_1.pk})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_chat_create_error_1(self):
    #     """Test create chat room w/ person who is not your friend"""
    #     api_path = '%s:chat:private-room-create' % settings.AVAILABLE_VERSIONS.get('current')
    #     response = self.client.post(reverse(api_path), data={'participant': self.user_4.id})
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.data.get('status_code'), api_exceptions.ArentFriendsError.extended_status_code)
    #
    def test_chat_create_error_2(self):
        """Test create chat room w/ person who is in your black list"""
        api_path = '%s:chat:private-room-create' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.post(reverse(api_path), data={'participant': self.user_3.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('status_code'), api_exceptions.AreFoesError.extended_status_code)

    def test_chat_create_error_3(self):
        """Test create chat room w/ person who was your friend but now in black list"""
        api_path = '%s:chat:private-room-create' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.post(reverse(api_path), data={'participant': self.user_5.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('status_code'), api_exceptions.AreFoesError.extended_status_code)

    def test_chat_create_error_4(self):
        """Test create chat room w/ myself"""
        api_path = '%s:chat:private-room-create' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.post(reverse(api_path), data={'participant': self.user.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('status_code'), api_exceptions.EqualIDError.extended_status_code)

