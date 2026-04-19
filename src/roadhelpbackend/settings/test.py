"""Test settings — fast, isolated, deterministic."""
import os

# Defaults that let the test suite run without a .env file.
os.environ.setdefault("SECRET_KEY", "test-secret-not-for-production")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("ALLOWED_HOSTS", "testserver,localhost")

from .base import *  # noqa: F401,F403,E402

DEBUG = False
TESTING = True

# Fast password hashing — speeds up fixtures creating users.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# In-process email backend so test assertions on mail.outbox work.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# In-memory cache — tests must not share state via Redis.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test",
    }
}

# In-memory channels layer
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

# Disable celery side effects
USE_CELERY = False
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Rate limit off in tests
RATELIMIT_ENABLE = False

# Never send real SMS / push from tests
USE_SMS = False
