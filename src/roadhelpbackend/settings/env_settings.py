"""
Environment loader. ALL defaults here are safe for dev and must be overridden
in prod via .env or the process environment.

Secrets (SECRET_KEY, DB_PASSWORD, SMS_PASSWORD, OTP_*, GOOGLE_APPLICATION_CREDENTIALS)
have NO defaults — missing them raises at startup. That's intentional.
"""
import environ

env = environ.Env(
    # Django core
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    CORS_ALLOWED_ORIGINS=(list, []),

    # Database
    DB_NAME=(str, "roadhelp"),
    DB_USER=(str, "roadhelp"),
    DB_HOST=(str, "localhost"),
    DB_PORT=(int, 5432),

    # Redis
    REDIS_URL=(str, "localhost"),
    REDIS_PORT=(int, 6379),
    REDIS_DB=(int, 0),

    # Localization
    TIME_ZONE=(str, "Europe/Moscow"),
    USE_TZ=(bool, True),
    USE_I18N=(bool, True),

    # Celery
    USE_CELERY=(bool, False),

    # Sentry
    SENTRY_DSN=(str, ""),

    # SMS
    SMS_SERVICE=(str, "https://smsc.ru/sys/send.php"),
    SMS_LOGIN=(str, ""),
    SMS_PASSWORD=(str, ""),
    SMS_SENDER=(str, "RoadHelper"),
    USE_SMS=(bool, False),
    TEST_SMS_CODE=(bool, False),
    APPROVE_ACCOUNT=(str, ""),
    SMS_SEND_DELAY=(int, 60),
    SMS_CODE_LENGTH=(int, 5),
    SMS_INPUT_ATTEMPTS=(int, 2),
    SMS_BLOCKING_PERIOD=(int, 86400),

    # OTP
    OTP_SERVICE=(str, "https://api.new-tel.net"),
    OTP_SERVER_KEY=(str, ""),
    OTP_SIGNATURE_KEY=(str, ""),

    # FCM
    GOOGLE_APPLICATION_CREDENTIALS=(str, ""),

    # Business rules
    REQUEST_RELEVANCE=(int, 30),
    DEFAULT_REQUEST_RADIUS=(int, 100000),
    NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS=(bool, True),
    LIMIT_UNREAD_MESSAGES=(int, 3),
    MESSAGES_UPDATE_PERIOD=(int, 15),
    NEWSLETTER_USERPROFILE_ID=(int, 1),

    # DRF
    PAGE_SIZE=(int, 15),

    # Uploads
    DATA_UPLOAD_MAX_MEMORY_SIZE=(int, 104857600),

    # Rate limits
    RATELIMIT_AUTH_PER_IP=(str, "5/m"),
    RATELIMIT_AUTH_PER_PHONE=(str, "3/h"),
)
