from autofixture import AutoFixture
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from account import models as account_models
from base import models
from catalog import models as catalog_models


class TestCatalog(APITestCase):
    VERSION = settings.AVAILABLE_VERSIONS.get('current')

    @classmethod
    def setUpClass(cls):
        """Set up for class"""
        print(f"\nStart test base app v{cls.VERSION}")
        print("==========")

    @classmethod
    def tearDownClass(cls):
        """Tear down for class"""
        print("==========")
        print(f"End test base app v{cls.VERSION}\n")

    def setUp(self):
        # Create City
        self.city = catalog_models.City.objects.create(name='City 1')

        # Create user
        self.user = account_models.User.objects.make(phone='+79000000000')

        # Create PushNotifications
        self.notification = models.PushNotification.objects.create(title='Push 1',
                                                                   description='Description',
                                                                   user=self.user)

    def test_news_list(self):
        """Test news list view"""

        # Create news
        AutoFixture(models.Newsletter).create(5)

        api_path = '%s:base:newsletter-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), models.Newsletter.objects.count())

    def test_news_detail(self):
        """Test news detail view"""

        # Create news
        news = AutoFixture(models.Newsletter).create(5)

        api_path = '%s:base:newsletter-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': news[0].id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notifications_list(self):
        """Test notifications list view"""
        # Authorize
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:base:pushnotification-list' % self.VERSION
        response = self.client.get(reverse(api_path))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), models.PushNotification.objects.count())

    def test_notifications_detail(self):
        """Test notifications detail view"""
        # Authorize
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        api_path = '%s:base:pushnotification-detail' % self.VERSION
        response = self.client.get(reverse(api_path, kwargs={'pk': self.notification.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
