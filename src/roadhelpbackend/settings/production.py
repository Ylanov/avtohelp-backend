"""Production server configuration."""

ALLOWED_HOSTS = [
    "avto-dobro.ru",
    "185.4.66.116",
]


DEBUG = False
USE_CELERY = True
USE_SMS = True  # Actual sms sending switcher
TEST_SMS_CODE = False
REDIS_URL = "redis://localhost:6379/13"
APPROVE_ACCOUNT = "+79189383399"

OTP_SERVICE = "https://api.new-tel.net"
OTP_SERVER_KEY = "317c850f18a7c6b9a3e1cdcc60ba0d3c6c1e6133ce836312"
OTP_SIGNATURE_KEY = "247c41f5e06bc112745ede424861bab6e6cf678d13d76124"

NEWSLETTER_USERPROFILE_ID = 50
