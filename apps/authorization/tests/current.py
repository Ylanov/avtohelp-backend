from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from authorization.models import SMSCode
from catalog.models import City


class TestCatalog(TestCase):
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
        # user data
        self.phone = '+79000000000'
        self.city = City.objects.create(name="Krasnodar")

    def test_verification(self):
        """Test view for verify user phone"""

        data = {"phone": self.phone, "city": self.city.id}

        api_path = '%s:authorization:verify' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.post(reverse(api_path), data=data)
        sms_code = SMSCode.objects.filter(phone=data.get('phone')).first()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(sms_code.status, sms_code.SENT)

    def test_authorization(self):
        """Test view for authorize user"""

        # verify
        api_path = '%s:authorization:verify' % settings.AVAILABLE_VERSIONS.get('current')
        self.client.post(reverse(api_path), data={"phone": self.phone, "city": self.city.id})
        sms_code = SMSCode.objects.filter(phone=self.phone).first()

        # authorize
        data = {"phone": self.phone, "code": int(sms_code.code)}
        api_path = '%s:authorization:auth' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.post(reverse(api_path), data=data)
        sms_code = SMSCode.objects.filter(phone=self.phone).first()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(sms_code.status, sms_code.ACTIVATED)

    def test_authorization_2(self):
        """Test view for authorize user"""

        # verify
        api_path = '%s:authorization:verify' % settings.AVAILABLE_VERSIONS.get('current')
        self.client.post(reverse(api_path), data={"phone": self.phone, "city": self.city.id})
        sms_code = SMSCode.objects.filter(phone=self.phone).first()

        # authorize
        data = {"phone": self.phone, "code": sms_code.code}
        api_path = '%s:authorization:auth' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.post(reverse(api_path), data=data)
        sms_code = SMSCode.objects.filter(phone=self.phone).first()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(sms_code.status, sms_code.ACTIVATED)

    def test_fail_authorization(self):
        """Test view for authorize user"""

        # verify
        api_path = '%s:authorization:verify' % settings.AVAILABLE_VERSIONS.get('current')
        self.client.post(reverse(api_path), data={"phone": self.phone, "city": self.city.id})
        SMSCode.objects.filter(phone=self.phone).first()

        # authorize
        data = {"phone": self.phone, "code": 1234}
        api_path = '%s:authorization:auth' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.post(reverse(api_path), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authorization_attempts(self):
        """Test authorization attempts"""

        # verify
        api_path = '%s:authorization:verify' % settings.AVAILABLE_VERSIONS.get('current')
        self.client.post(reverse(api_path), data={"phone": self.phone, "city": self.city.id})
        SMSCode.objects.filter(phone=self.phone).first()

        # authorize
        data = {"phone": self.phone, "code": 1234}
        api_path = '%s:authorization:auth' % settings.AVAILABLE_VERSIONS.get('current')
        for i in range(settings.SMS_INPUT_ATTEMPTS):
            self.client.post(reverse(api_path), data=data)
        response = self.client.post(reverse(api_path), data=data)
        self.assertEqual(response.status_code, status.HTTP_423_LOCKED)
