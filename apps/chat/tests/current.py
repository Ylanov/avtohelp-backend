from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from account.models import User
from userprofile.models import BlackList, FriendList, FriendRequest
from chat.models import ChatRoom


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

        # Add user_1 to friend list
        friend_request = FriendRequest.objects.make(owner=self.user, user=self.user_1)
        FriendList.objects.create(owner=self.user, friend=self.user_1, request=friend_request)

        # Add user_2 to black list
        BlackList.objects.create(owner=self.user, foe=self.user_2)

        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_chat_list(self):
        """Test view for getting list of chats"""
        # Create Chat Room
        ChatRoom.objects.create(initiator=self.user, participant=self.user_1, is_public=False)
        ChatRoom.objects.create(initiator=self.user, participant=self.user_2, is_public=False)

        api_path = '%s:chat:room-list' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), ChatRoom.objects.by_participant(self.user).count())

    def test_chat_create(self):
        """Test create chat room"""
        api_path = '%s:chat:room-create' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.post(reverse(api_path, kwargs={'participant': self.user_1}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_chat_create_error_1(self): pass

    def test_chat_create_error_2(self): pass

    def test_chat_create_error_3(self): pass
