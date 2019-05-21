from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from account.models import User
from catalog.models import City
from car.models import CarColor, CarMark, CarModel, Car
from userprofile.models import (Profile, BlackList, FriendList,
                                FriendRequest, ProfileCar,
                                ProfileGallery)


class TestProfile(APITestCase):
    VERSION = settings.AVAILABLE_VERSIONS.get('current')

    @classmethod
    def setUpClass(cls):
        """Set up for class"""
        print(f"\nStart test profile app v{cls.VERSION}")
        print("==========")

    @classmethod
    def tearDownClass(cls):
        """Tear down for class"""
        print("==========")
        print(f"End test profile app v{cls.VERSION}\n")

    def setUp(self):
        # Create cities
        self.city_1 = City.objects.create(name='Krasnodar')
        self.city_2 = City.objects.create(name='Kaliningrad')
        self.city_3 = City.objects.create(name='Novosibirsk')

        # Create users
        self.user_1 = User.objects.make(phone='+79000000001')

        # Create car brands
        self.toyota = CarMark.objects.create(name='Toyota')
        self.nissan = CarMark.objects.create(name='Nissan')

        # Create car models
        self.toyota_model = CarModel.objects.create(name='Supra', mark=self.toyota)
        self.nissan_model = CarModel.objects.create(name='350Z', mark=self.nissan)

        # Create car colors
        self.color_1 = CarColor.objects.create(name='White')

        # Create user cars
        self.car_1 = Car.objects.create(mark=self.toyota,
                                        car_model=self.toyota_model)
        self.car_2 = Car.objects.create(mark=self.nissan,
                                        car_model=self.nissan_model)
        self.car_user_1 = ProfileCar.objects.create(owner=self.user_1,
                                                    car=self.car_1,
                                                    color=self.color_1,
                                                    license_plate='aaa123aa 70')

    def test_retrieving_profile(self):
        """Test view for retrieving user profile"""

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:my-profile-detail' % self.VERSION
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

        api_path = '%s:userprofile:my-profile-detail' % self.VERSION
        response = self.client.patch(reverse(api_path), data=data)
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

        api_path = '%s:userprofile:my-profile-detail' % self.VERSION
        response = self.client.put(reverse(api_path), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieving_profile_unauthorized_user(self):
        """Test view for retrieving unauthorized user profile"""

        api_path = '%s:userprofile:my-profile-detail' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profiles_list_1(self):
        """Common test for retrieving profiles list"""

        # Create additional users
        u_1 = User.objects.make(phone='+79000000002')
        u_1.profile.first_name, u_1.profile.last_name = 'Test', 'Testovich'
        u_1.profile.save()

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:profile-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), Profile.objects.exclude(user=self.user_1).count())

    def test_profiles_list_2(self):
        """
        Test for retrieving profiles list w/o blacked profiles
            Users: user_1, user_2, user_3
            Authorized user: user_1
            Users in BlackList: user_2
            Result retrieving profile list: user_3
        """

        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        user_3 = User.objects.make(phone='+79000000003')
        user_3.profile.first_name, user_3.profile.last_name = 'Test', 'Testovich'
        user_3.profile.save()

        # Put user_2 in BlackList
        BlackList.objects.create(owner=self.user_1, foe=user_2)

        api_path = '%s:userprofile:profile-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 1)

    def test_profiles_list_3(self):
        """
        Test for retrieving profiles list w/ friends profiles
            Users: user_1, user_2, user_3
            Authorized user: user_1
            Users in FriendList: user_2
            Result retrieving profile list: user_2, user_3
        """

        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        user_3 = User.objects.make(phone='+79000000003')
        user_3.profile.first_name, user_3.profile.last_name = 'Test', 'Testovich'
        user_3.profile.save()

        # Put user_3 in FriendList
        request = FriendRequest.objects.create(owner=self.user_1, invited=user_2, approved=True)
        FriendList.objects.create(owner=self.user_1, friend=user_2, request=request)

        api_path = '%s:userprofile:profile-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 2)

    def test_profiles_list_4(self):
        """
        Test for retrieving profiles list w/o friends profiles and blacked profiles
            Users: user_1, user_2, user_3, user_4
            Authorized user: user_1
            Users in FriendList: user_2
            Users in BlackList: user_3
            Result retrieving profile list: user_2, user_4
        """

        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        user_3 = User.objects.make(phone='+79000000003')
        user_3.profile.first_name, user_3.profile.last_name = 'Test', 'Testovich'
        user_3.profile.save()

        user_4 = User.objects.make(phone='+79000000004')
        user_4.profile.first_name, user_4.profile.last_name = 'Test', 'Testovich'
        user_4.profile.save()

        # Put user_2 in BlackList
        BlackList.objects.create(owner=self.user_1, foe=user_2)

        # Put user_3 in FriendList
        request = FriendRequest.objects.create(owner=self.user_1, invited=user_3, approved=True)
        FriendList.objects.create(owner=self.user_1, friend=user_3, request=request)

        api_path = '%s:userprofile:profile-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 2)

    def test_profile_detail(self):
        """Test profile detail"""

        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        api_path = '%s:userprofile:profile-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': user_2.profile.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), user_2.profile.id)

    def test_my_profile_detail(self):
        """Test my profile detail"""
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:my-profile-detail' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_detail_1(self):
        """Test get wrong profile detail"""

        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        User.objects.make(phone='+79000000002')

        api_path = '%s:userprofile:profile-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': 420}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_friend_requests_1(self):
        """
        Get all friend requests FROM user
        """

        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        user_3 = User.objects.make(phone='+79000000003')
        user_3.profile.first_name, user_3.profile.last_name = 'Test', 'Testovich'
        user_3.profile.save()

        # Put user_3 in FriendList
        request = FriendRequest.objects.create(owner=self.user_1, invited=user_2, approved=True)
        FriendList.objects.create(owner=self.user_1, friend=user_3, request=request)

        api_path = '%s:userprofile:my-friendrequest-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), FriendRequest.objects.all().not_approved().count())

    def test_my_friend_request_detail(self):
        """
        Get all friend requests FROM user
        """

        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        user_3 = User.objects.make(phone='+79000000003')
        user_3.profile.first_name, user_3.profile.last_name = 'Test', 'Testovich'
        user_3.profile.save()

        # Put user_3 in FriendList
        request = FriendRequest.objects.create(owner=self.user_1, invited=user_2, approved=True)
        FriendList.objects.create(owner=self.user_1, friend=user_3, request=request)

        api_path = '%s:userprofile:my-friendrequest-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': request.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('person').get('id'), user_2.profile.id)

    def test_friend_request_to_user(self):
        """
        Get all friend requests TO user
        """
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        user_3 = User.objects.make(phone='+79000000003')
        user_3.profile.first_name, user_3.profile.last_name = 'Test', 'Testovich'
        user_3.profile.save()

        # Put user_3 in FriendList
        FriendRequest.objects.create(owner=user_2, invited=self.user_1, approved=False)
        FriendRequest.objects.create(owner=user_3, invited=self.user_1, approved=True)

        api_path = '%s:userprofile:friendrequest-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), FriendRequest.objects.not_approved().count())

    def test_friend_request_to_user_2(self):
        """
        Get all friend requests TO user
        """
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        user_3 = User.objects.make(phone='+79000000003')
        user_3.profile.first_name, user_3.profile.last_name = 'Test', 'Testovich'
        user_3.profile.save()

        # Put user_3 in FriendList
        FriendRequest.objects.create(owner=user_2, invited=self.user_1, approved=True)
        FriendRequest.objects.create(owner=user_3, invited=self.user_1, approved=True)

        api_path = '%s:userprofile:friendrequest-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), FriendRequest.objects.not_approved().count())

    def test_friend_request_to_user_3(self):
        """
        Get all friend requests TO user
        """
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        user_3 = User.objects.make(phone='+79000000003')
        user_3.profile.first_name, user_3.profile.last_name = 'Test', 'Testovich'
        user_3.profile.save()

        # Put user_3 in FriendList
        FriendRequest.objects.create(owner=user_2, invited=self.user_1, approved=False)
        FriendRequest.objects.create(owner=user_3, invited=self.user_1, approved=False)

        api_path = '%s:userprofile:friendrequest-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), FriendRequest.objects.not_approved().count())

    def test_friend_request_to_user_4(self):
        """
        Get all friend requests TO user
        """
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        user_3 = User.objects.make(phone='+79000000003')
        user_3.profile.first_name, user_3.profile.last_name = 'Test', 'Testovich'
        user_3.profile.save()

        # Put user_3 in FriendList
        FriendRequest.objects.create(owner=user_2, invited=self.user_1, approved=False)
        FriendRequest.objects.create(owner=user_3, invited=self.user_1, approved=True)

        api_path = '%s:userprofile:friendrequest-list' % self.VERSION
        response = self.client.get(reverse(api_path), data={'person_id': user_2.profile.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), FriendRequest.objects.not_approved().to_me(
            self.user_1).filter(owner=user_2).count())

    def test_friend_request_to_user_5(self):
        """
        Get all friend requests FROM user
        """
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        user_3 = User.objects.make(phone='+79000000003')
        user_3.profile.first_name, user_3.profile.last_name = 'Test', 'Testovich'
        user_3.profile.save()

        # Put user_3 in FriendList
        FriendRequest.objects.create(owner=self.user_1, invited=user_2, approved=False)
        FriendRequest.objects.create(owner=self.user_1, invited=user_3, approved=True)

        api_path = '%s:userprofile:my-friendrequest-list' % self.VERSION
        response = self.client.get(reverse(api_path), data={'person_id': user_2.profile.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), FriendRequest.objects.not_approved().from_me(
            self.user_1).filter(invited=user_2).count())

    def test_friend_request_to_user_detail(self):
        """
        Get all friend requests TO user
        """
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        # Put user_3 in FriendList
        request = FriendRequest.objects.create(owner=user_2, invited=self.user_1)

        api_path = '%s:userprofile:friendrequest-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': request.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('person').get('id'), user_2.profile.id)

    def test_friend_request_to_user_approve(self):
        """
        Get all friend requests TO usertest_my_friend_request_detail
        """
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        request = FriendRequest.objects.create(owner=user_2, invited=self.user_1)

        api_path = '%s:userprofile:friendrequest-approve' % self.VERSION
        response = self.client.patch(reverse(api_path, kwargs={'pk': request.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('approved'), True)

    def test_delete_outgoing_request(self):
        """
        Test delete outgoing friend request
        """
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        request = FriendRequest.objects.create(owner=self.user_1, invited=user_2)

        api_path = '%s:userprofile:my-friendrequest-delete' % self.VERSION
        response = self.client.delete(reverse(api_path, kwargs={'pk': request.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_incoming_request(self):
        """
        Test delete incoming friend request
        """
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        request = FriendRequest.objects.create(owner=user_2, invited=self.user_1)

        api_path = '%s:userprofile:friendrequest-delete' % self.VERSION
        response = self.client.delete(reverse(api_path, kwargs={'pk': request.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_friend_list(self):
        """Test for retrieving user friends"""
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        user_3 = User.objects.make(phone='+79000000003')
        user_3.profile.first_name, user_3.profile.last_name = 'Test', 'Testovich'
        user_3.profile.save()

        # Create friend request for user_3
        FriendRequest.objects.create(owner=user_2, invited=self.user_1, approved=False)
        friend_request = FriendRequest.objects.create(owner=user_3, invited=self.user_1, approved=True)

        # Put user_3 to friend list
        FriendList.objects.create(owner=user_3, friend=self.user_1, request=friend_request)

        api_path = '%s:userprofile:friendrequest-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), FriendList.objects.common(self.user_1).count())

    def test_friend_list_1(self):
        """Test for retrieving user friends"""
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        user_3 = User.objects.make(phone='+79000000003')
        user_3.profile.first_name, user_3.profile.last_name = 'Test', 'Testovich'
        user_3.profile.save()

        # Create friend request for user_3
        friend_request = FriendRequest.objects.create(owner=user_2, invited=self.user_1, approved=False)

        # Put user_3 to friend list
        FriendList.objects.create(owner=user_3, friend=self.user_1, request=friend_request)

        api_path = '%s:userprofile:friendrequest-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), FriendList.objects.common(self.user_1).count())

    def test_friend_list_3(self):
        """Test for retrieving user friends"""
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        # Create friend request for user_2
        friend_request = FriendRequest.objects.create(owner=user_2, invited=self.user_1, approved=True)

        # Put user_2 to friend list
        FriendList.objects.create(owner=user_2, friend=self.user_1, request=friend_request)

        api_path = '%s:userprofile:friendlist-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), FriendList.objects.common(self.user_1).count())

    def test_remove_friend_from_friendlist(self):
        """Test remove friend from friendlist"""
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        # Put user_2 to friends
        friend_request = FriendRequest.objects.create(owner=self.user_1, invited=user_2, approved=True)
        friend = FriendList.objects.create(owner=self.user_1, friend=user_2, request=friend_request)

        api_path = '%s:userprofile:friendlist-delete' % self.VERSION
        response = self.client.delete(reverse(api_path, kwargs={'profile_id': user_2.profile.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_remove_friend_from_friendlist_1(self):
        """Test remove friend from friendlist"""
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        # Put user_2 to friends
        friend_request = FriendRequest.objects.create(owner=self.user_1, invited=user_2, approved=True)
        friend = FriendList.objects.create(owner=self.user_1, friend=user_2, request=friend_request)

        api_path = '%s:userprofile:friendlist-delete' % self.VERSION
        response = self.client.delete(reverse(api_path, kwargs={'profile_id': 420}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_blacklist_requests(self):
        """
        Get all user blacklist requests
        """
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        # Before request
        blacked_before = BlackList.objects.count()

        # Put user_2 in BlackList
        BlackList.objects.create(owner=self.user_1, foe=user_2)
        blacked_after = BlackList.objects.count()

        api_path = '%s:userprofile:blacklistrequest-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(blacked_before, blacked_after)
        self.assertEqual(response.data.get('count'), blacked_after)

    def test_blacklist_detail_request_to_user(self):
        """
        Get detail user blacklist requests
        """
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        # Put user_2 in BlackList
        black_list = BlackList.objects.create(owner=self.user_1, foe=user_2)

        api_path = '%s:userprofile:blacklistrequest-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': black_list.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), black_list.id)

    def test_remove_user_blacklist_request(self):
        """
        Remove user black list
        """
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        # Put user_2 in BlackList
        black_list = BlackList.objects.create(owner=self.user_1, foe=user_2)

        api_path = '%s:userprofile:blacklistrequest-delete' % self.VERSION
        response = self.client.delete(reverse(api_path, kwargs={'profile_id': user_2.profile.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_blacklist_request(self):
        """
        Create user black list
        """
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        # Before request
        blacked_before = BlackList.objects.count()

        api_path = '%s:userprofile:blacklistrequest-create' % self.VERSION
        response = self.client.post(reverse(api_path), data={'profile': user_2.profile.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(blacked_before, BlackList.objects.count())

    def test_add_to_friend(self):
        """Add user to friend list"""
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        api_path = '%s:userprofile:friendrequest-create' % self.VERSION
        response = self.client.post(reverse(api_path), data={'profile': user_2.profile.id})
        request_id = response.data.get('id')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Authorize user_2
        self.token, created = Token.objects.get_or_create(user=user_2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:friendrequest-approve' % self.VERSION
        response = self.client.patch(reverse(api_path, kwargs={'pk': request_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check count of friends
        api_path = '%s:userprofile:friendlist-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), FriendList.objects.common(user_2).count())

    def test_add_to_friend_1(self):
        """Add user to friend list"""
        # Authorize user_1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        api_path = '%s:userprofile:friendrequest-create' % self.VERSION
        response = self.client.post(reverse(api_path), data={'profile': user_2.profile.id})
        request_id = response.data.get('id')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Authorize user_2
        self.token, created = Token.objects.get_or_create(user=user_2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:friendrequest-create' % self.VERSION
        response = self.client.post(reverse(api_path), data={'profile': self.user_1.profile.id})
        request_id = response.data.get('id')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check count of friends
        api_path = '%s:userprofile:friendlist-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), FriendList.objects.common(user_2).count())

    def test_profile_cars(self):
        """Common test for retrieving list of profile cars"""

        # Create second car
        ProfileCar.objects.create(owner=self.user_1,
                                  car=self.car_2,
                                  color=self.color_1,
                                  license_plate='xxx123xx 70')

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:profile-car-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), ProfileCar.objects.filter(owner=self.user_1).count())

    def test_profile_car_detail(self):
        """Common test for retrieving detail of profile car"""

        # Create second car
        car_2 = ProfileCar.objects.create(owner=self.user_1,
                                          car=self.car_2,
                                          color=self.color_1,
                                          license_plate='xxx123xx 70')

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:profile-car-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': car_2.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), car_2.id)

    def test_profile_car_detail_update(self):
        """Common test for retrieving detail of profile car"""

        # Create second car
        car_2 = ProfileCar.objects.create(owner=self.user_1,
                                          car=self.car_2,
                                          color=self.color_1,
                                          license_plate='xxx123xx 70')

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:profile-car-detail' % self.VERSION
        response = self.client.patch(reverse(api_path, kwargs={'pk': car_2.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('license_plate'), ProfileCar.objects.get(id=car_2.id).license_plate)

    def test_profile_car_add(self):
        """Common test for link a new car to profile"""

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        data = {
            "color": self.color_1.id,
            "car": self.car_1.id,
            "license_plate": "yyy123yy 100"
        }

        api_path = '%s:userprofile:profile-car-create' % self.VERSION
        response = self.client.post(reverse(api_path), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_profile_car_delete(self):
        """Common test delete profile car"""

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        api_path = '%s:userprofile:profile-car-delete' % self.VERSION
        response = self.client.delete(reverse(api_path, kwargs={'pk': self.car_user_1.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_profile_gallery(self):
        """Common test for retrieving list of profile gallery images"""

        # Create images for gallery
        ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:profile-gallery-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), ProfileGallery.objects.count())

    def test_profile_gallery_1(self):
        """Common test for retrieving list of profile gallery images"""

        # Create images for gallery
        ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)

        api_path = '%s:userprofile:profile-gallery-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_gallery_2(self):
        """Common test for retrieving list of profile gallery images"""

        # Create additional user
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        # Create images for gallery
        ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=user_2.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)

        # Authorize user 2
        self.token, created = Token.objects.get_or_create(user=user_2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:profile-gallery-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), ProfileGallery.objects.all().count())

    def test_profile_gallery_detail(self):
        """Common test for retrieving detail of profile gallery object"""

        # Create images for gallery
        profile_image = ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:profile-gallery-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': profile_image.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), profile_image.id)

    def test_profile_gallery_detail_1(self):
        """Common test for retrieving detail of profile gallery object"""

        # Create additional user
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        # Create images for gallery
        profile_image = ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=user_2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:profile-gallery-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': profile_image.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_profile_gallery_detail_2(self):
        """Common test for retrieving detail of profile gallery object"""

        # Create images for gallery
        profile_image = ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)

        api_path = '%s:userprofile:profile-gallery-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': profile_image.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_gallery_detail_3(self):
        """Common test for retrieving detail of profile gallery object"""

        # Create images for gallery
        ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:profile-gallery-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': 420}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_profile_gallery_delete(self):
        """Common test delete profile gallery object"""

        # Create images for gallery
        profile_image = ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)
        gallery_count_old = ProfileGallery.objects.by_user(self.user_1).count()

        # Authorize user 1
        self.token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:profile-gallery-delete' % self.VERSION
        response = self.client.delete(reverse(api_path, kwargs={'pk': profile_image.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotEqual(gallery_count_old, ProfileGallery.objects.by_user(self.user_1).count())

    def test_profile_gallery_delete_1(self):
        """Common test delete profile gallery object"""

        # Create additional user
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        # Create images for gallery
        profile_image = ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)

        # Authorize user 2
        self.token, created = Token.objects.get_or_create(user=user_2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:userprofile:profile-gallery-delete' % self.VERSION
        response = self.client.delete(reverse(api_path, kwargs={'pk': profile_image.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_profile_gallery_delete_2(self):
        """Common test delete profile gallery object"""

        # Create images for gallery
        profile_image = ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)
        ProfileGallery.objects.create(profile=self.user_1.profile)

        api_path = '%s:userprofile:profile-gallery-delete' % self.VERSION
        response = self.client.delete(reverse(api_path, kwargs={'pk': profile_image.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_annotated_field_friend(self):
        """Test case for correct value of annotated field friend"""
        # Authorize user_1
        token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        # Added user_2 to friend list
        friend_request = FriendRequest.objects.create(owner=user_2, invited=self.user_1, approved=True)
        FriendList.objects.create(owner=user_2, friend=self.user_1, request=friend_request)

        api_path = '%s:userprofile:profile-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': user_2.profile.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('friend'), True)

    def test_annotated_field_friend_1(self):
        """Test case for correct value of annotated field friend"""
        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        # Authorize user_1
        token, created = Token.objects.get_or_create(user=user_2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        # Added user_1 to friend list
        friend_request = FriendRequest.objects.create(owner=self.user_1, invited=user_2, approved=True)
        FriendList.objects.create(owner=self.user_1, friend=user_2, request=friend_request)

        api_path = '%s:userprofile:profile-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': self.user_1.profile.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('friend'), True)

    def test_annotated_field_foe(self):
        """Test case for correct value of annotated field foe"""
        # Authorize user_1
        token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        # Added user_2 to black list
        BlackList.objects.create(owner=self.user_1, foe=user_2)

        api_path = '%s:userprofile:profile-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': user_2.profile.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('foe'), True)

    def test_annotated_field_foe_1(self):
        """Test case for correct value of annotated field foe"""
        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        # Authorize user_1
        token, created = Token.objects.get_or_create(user=user_2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        # Added user_2 to black list
        BlackList.objects.create(owner=user_2, foe=self.user_1)

        api_path = '%s:userprofile:profile-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': self.user_1.profile.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('foe'), True)

    def test_annotated_field_friend_request(self):
        """Test case for correct value of annotated field friend_request"""
        # Authorize user_1
        token, created = Token.objects.get_or_create(user=self.user_1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        # Create additional users
        user_2 = User.objects.make(phone='+79000000002')
        user_2.profile.first_name, user_2.profile.last_name = 'Test', 'Testovich'
        user_2.profile.save()

        # Create friend request for user_2
        FriendRequest.objects.create(owner=self.user_1, invited=user_2)

        api_path = '%s:userprofile:profile-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': user_2.profile.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('friend_request'), True)
