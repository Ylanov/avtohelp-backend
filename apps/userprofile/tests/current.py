from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from account.models import User
from catalog.models import City


class TestCatalog(APITestCase):
    VERSION = settings.AVAILABLE_VERSIONS.get('current')

    @classmethod
    def setUpClass(cls):
        """Set up for class"""
        print(f"\nStart test authorization app v{cls.VERSION}")
        print("==========")

    @classmethod
    def tearDownClass(cls):
        """Tear down for class"""
        print("==========")
        print(f"End test authorization app v{cls.VERSION}\n")

    def setUp(self):
        # Create cities
        self.city_1 = City.objects.create(name='Krasnodar')
        self.city_2 = City.objects.create(name='Kaliningrad')
        self.city_3 = City.objects.create(name='Novosibirsk')

        # Create users
        self.user_1 = User.objects.make(phone='+79000000001')
        self.user_2 = User.objects.make(phone='+79000000002')

    def test_retrieving_profile(self):
        """Test view for retrieving user profile"""

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:profile' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), self.user_1.profile.id)

    def test_fill_profile_partial(self):
        """Test view for PATCH-update user profile"""

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Updated data
        data = {
            "first_name": "First name",
            "last_name": "Last name",
        }

        api_path = '%s:userprofile:profile' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.patch(reverse(api_path), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), self.user_1.profile.id)
        for field in data:
            self.assertEqual(response.data.get(field), data[field])

    def test_fill_profile(self):
        """Test view for PUT-update user profile"""

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Updated data
        data = {
            "first_name": "First name",
            "last_name": "Last name",
            "middle_name": "Middle name"
        }

        api_path = '%s:userprofile:profile' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.put(reverse(api_path), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), self.user_1.profile.id)
        for field in data:
            self.assertEqual(response.data.get(field), data[field])

    def test_error_fill_profile(self):
        """Test view for PUT-update user profile"""

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Updated data
        data = {
            "first_name": "First name",
            "last_name": "Last name",
        }

        api_path = '%s:userprofile:profile' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.put(reverse(api_path), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieving_profile_unauthorized_user(self):
        """Test view for retrieving unauthorized user profile"""

        api_path = '%s:userprofile:profile' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
