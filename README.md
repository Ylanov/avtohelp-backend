# RoadHelp backend

Backend for the RoadHelp ("автопомощь на дороге") mobile app — mutual roadside
assistance. Drivers post a help request with a geo-location, nearby users are
notified via FCM push, and they chat/call.

## Stack

- Python 3.12, Django 5.2 LTS
- DRF 3.15 + drf-spectacular (OpenAPI)
- PostgreSQL 15 + PostGIS 3.4 (geo)
- Redis 7 (cache, Celery broker, Channels layer)
- Celery 5 (async tasks) + django-celery-beat
- Channels 4 + daphne (WebSocket chat)
- Firebase Admin SDK (FCM push)
- gunicorn 23 (WSGI for REST) + daphne (ASGI for WS)

## Layout

```
src/
├── roadhelpbackend/       # Django project: settings/ (base,dev,prod,test), urls/, routing.py
├── authorization/         # phone SMS verification + token auth
├── account/               # custom User model (phone as unique field)
├── userprofile/           # Profile, ProfileLocation, ProfileCar, friends, blacklist, FCM devices
├── order/                 # AssistanceRequest (the main feature)
├── chat/                  # ChatRoom + ChatMessage + WebSocket consumer
├── car/                   # CarMark / CarModel / CarColor / CarService catalogues
├── catalog/               # City list
├── base/                  # Newsletters, push-notification records, GeneralInfo aggregator
└── utils/                 # shared mixins, api_exceptions, push helper

docs/
└── API_CONTRACT.md        # FROZEN contract consumed by the Android bug_fix branch

deploy/
├── nginx/avtohelp24.conf  # reverse proxy (HTTP→HTTPS, WSS to daphne)
└── README.md              # step-by-step cloud deploy guide
```

## Local development

```bash
cp .env.example .env                     # fill secrets
docker compose up -d --build
docker compose exec api python src/manage.py migrate
docker compose exec api python src/manage.py createsuperuser
```

Services:

- REST API:  http://localhost:8000/api/v1.0.0/
- Admin:     http://localhost:8000/admin/
- Health:    http://localhost:8000/health/
- Swagger:   http://localhost:8000/swagger/
- Redoc:     http://localhost:8000/redoc/
- WebSocket: ws://localhost:8001/chat/stream

## Running the test suite

```bash
docker compose exec api pytest -m contract
```

Contract tests (`src/tests/test_contract_*.py`) exercise every endpoint the
Android app relies on. They are the regression gate when upgrading
dependencies — keep them green.

## Production

See [deploy/README.md](deploy/README.md) for the full step-by-step bring-up
of `avtohelp24.ru` (nginx + Let's Encrypt + docker compose).

## API contract

All Android-facing routes, request bodies, and response shapes are frozen in
[docs/API_CONTRACT.md](docs/API_CONTRACT.md). Do not change anything listed
there without a synchronised Android release.

## Environment variables

Full list with defaults lives in `.env.example`. A summary:

| Group       | Vars                                                                 |
|-------------|----------------------------------------------------------------------|
| Django core | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DJANGO_SETTINGS_MODULE`     |
| Database    | `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`            |
| Redis       | `REDIS_URL`, `REDIS_PORT`, `REDIS_DB`                                |
| Celery      | `USE_CELERY`                                                          |
| SMS         | `SMS_SERVICE`, `SMS_LOGIN`, `SMS_PASSWORD`, `SMS_SENDER`, `USE_SMS`, `TEST_SMS_CODE`, `APPROVE_ACCOUNT` |
| OTP call    | `OTP_SERVICE`, `OTP_SERVER_KEY`, `OTP_SIGNATURE_KEY`                  |
| FCM         | `GOOGLE_APPLICATION_CREDENTIALS` (path to Firebase service-account JSON) |
| Rate limit  | `RATELIMIT_AUTH_PER_IP`, `RATELIMIT_AUTH_PER_PHONE`                  |
| Observability | `SENTRY_DSN`                                                       |
| Business    | `REQUEST_RELEVANCE`, `DEFAULT_REQUEST_RADIUS`, `LIMIT_UNREAD_MESSAGES`, `MESSAGES_UPDATE_PERIOD`, `NEWSLETTER_USERPROFILE_ID`, `NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS` |

## License

Proprietary.
