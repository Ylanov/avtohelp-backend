"""Local developer settings — DEBUG on, console email, permissive CORS."""
from .base import *  # noqa: F401,F403

DEBUG = True

# Dev: allow any browser origin so local web admin / Swagger UI work.
CORS_ALLOWED_ORIGIN_REGEXES = [r"^https?://localhost(:\d+)?$", r"^https?://127\.0\.0\.1(:\d+)?$"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable rate-limiting in dev so you can hammer endpoints from Postman.
RATELIMIT_ENABLE = False

INTERNAL_IPS = ["127.0.0.1"]
