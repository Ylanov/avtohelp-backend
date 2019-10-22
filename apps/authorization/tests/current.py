from time import sleep

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from authorization.models import SMSCode
from utils import api_exceptions
from utils import custom_statuses


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

    def test_verification(self):
        """Test view for verify user phone"""

        data = {"phone": self.phone}

        api_path = '%s:authorization:verify' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.post(reverse(api_path), data=data)
        sms_code = SMSCode.objects.filter(phone=self.phone).first()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(sms_code.status, sms_code.SENT)

    def test_verification_cooldown(self):
        """Test for verification cooldown when requests sends often"""
        data = {"phone": self.phone}

        api_path = '%s:authorization:verify' % settings.AVAILABLE_VERSIONS.get('current')
        self.client.post(reverse(api_path), data=data)
        response = self.client.post(reverse(api_path), data=data)
        self.assertEqual(response.status_code, custom_statuses.HTTP_420_ENHACE_YOUR_CALM)

    def test_verification_cooldown_delay(self):
        """Test for verification cooldown when requests sends after some delay"""
        data = {"phone": self.phone}

        api_path = '%s:authorization:verify' % settings.AVAILABLE_VERSIONS.get('current')
        self.client.post(reverse(api_path), data=data)
        sleep(settings.SMS_SEND_DELAY)
        response = self.client.post(reverse(api_path), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authorization(self):
        """
        Test view for authorize user
        In this case verification code is in INTEGER representation
        """
        # verify
        api_path = '%s:authorization:verify' % settings.AVAILABLE_VERSIONS.get('current')
        self.client.post(reverse(api_path), data={"phone": self.phone})
        sms_code = SMSCode.objects.filter(phone=self.phone).first()

        # authorize
        data = {"phone": self.phone, "code": int(sms_code.code)}
        api_path = '%s:authorization:auth' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.post(reverse(api_path), data=data)
        sms_code = SMSCode.objects.filter(phone=self.phone).first()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(sms_code.status, sms_code.ACTIVATED)

    def test_authorization_2(self):
        """
        Test view for authorize user
        In this case verification code is in STRING representation
        """

        # verify
        api_path = '%s:authorization:verify' % settings.AVAILABLE_VERSIONS.get('current')
        self.client.post(reverse(api_path), data={"phone": self.phone})
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
        self.client.post(reverse(api_path), data={"phone": self.phone})
        SMSCode.objects.filter(phone=self.phone).first()

        # authorize
        data = {"phone": self.phone, "code": 1234}
        api_path = '%s:authorization:auth' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.post(reverse(api_path), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('status_code'), api_exceptions.CodeIsNotAcceptedError.extended_status_code)

    def test_authorization_attempts(self):
        """Test authorization attempts"""

        # verify
        api_path = '%s:authorization:verify' % settings.AVAILABLE_VERSIONS.get('current')
        self.client.post(reverse(api_path), data={"phone": self.phone})
        SMSCode.objects.filter(phone=self.phone).first()

        # authorize
        data = {"phone": self.phone, "code": 1234}
        api_path = '%s:authorization:auth' % settings.AVAILABLE_VERSIONS.get('current')
        for i in range(settings.SMS_INPUT_ATTEMPTS):
            self.client.post(reverse(api_path), data=data)
        response = self.client.post(reverse(api_path), data=data)
        self.assertEqual(response.status_code, status.HTTP_423_LOCKED)
        self.assertEqual(response.data.get('detail'), api_exceptions.TemporaryLockError.default_detail)

    def test_nonexisted_user_with_requested_phone(self):
        """Test send request with non-existed user phone number"""
        # verify
        api_path = '%s:authorization:verify' % settings.AVAILABLE_VERSIONS.get('current')
        self.client.post(reverse(api_path), data={"phone": self.phone})
        sms_code = SMSCode.objects.filter(phone=self.phone).first()

        # authorize
        data = {"phone": "+79998887766", "code": int(sms_code.code)}
        api_path = '%s:authorization:auth' % settings.AVAILABLE_VERSIONS.get('current')
        response = self.client.post(reverse(api_path), data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get('detail'), api_exceptions.UserNotFound.default_detail)
