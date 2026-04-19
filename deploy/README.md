# Production deploy — avtohelp24.ru

Step-by-step bring-up on a fresh cloud server.

## 0. Server requirements

- Linux (Ubuntu 22.04 LTS or newer recommended)
- Public IPv4, domain `avtohelp24.ru` A-record → this IP
- Ports 80 + 443 open in firewall
- Docker Engine 24+ and the compose plugin
- ~4 GB RAM minimum, ~20 GB disk

## 1. Clone and prepare

```bash
cd /opt
git clone https://github.com/<your>/roadhelpbackend.git avtohelp
cd avtohelp
git checkout claude/vigorous-tereshkova-c18f3e   # or main once merged
```

## 2. Secrets

```bash
cp .env.example .env
# Edit .env and fill in:
#   SECRET_KEY            -> python -c "import secrets; print(secrets.token_urlsafe(64))"
#   DB_PASSWORD           -> strong random password
#   SMS_LOGIN, SMS_PASSWORD       (SMSC.ru account)
#   OTP_SERVER_KEY, OTP_SIGNATURE_KEY  (new-tel.net account)
#   SENTRY_DSN            -> optional
```

Set:

```
ALLOWED_HOSTS=avtohelp24.ru,www.avtohelp24.ru
DJANGO_SETTINGS_MODULE=roadhelpbackend.settings.prod
DEBUG=false
USE_SMS=true
TEST_SMS_CODE=false
USE_CELERY=true
```

Place the Firebase service-account JSON for FCM:

```bash
mkdir -p ./secrets
# upload your Firebase admin SDK key as:
cp ~/Downloads/avtohelp-firebase-adminsdk.json ./secrets/fcm-service-account.json
chmod 600 ./secrets/fcm-service-account.json
```

And set in `.env`:

```
GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/fcm-service-account.json
```

## 3. First-time bring-up (HTTP-only, to obtain TLS cert)

Temporarily comment the `https` server block in `deploy/nginx/avtohelp24.conf`
(or deploy a minimal HTTP-only conf). Then:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d db redis
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d api ws celery celery-beat
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d nginx
```

Check API is up:

```bash
curl http://avtohelp24.ru/health/
# {"status": "ok"}
```

## 4. Obtain Let's Encrypt cert

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot \
    certonly --webroot -w /var/www/certbot \
    -d avtohelp24.ru -d www.avtohelp24.ru \
    --email you@example.com --agree-tos --no-eff-email
```

Re-enable the `https` block, then:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart nginx
```

Verify:

```bash
curl https://avtohelp24.ru/health/
```

## 5. Migrate and create a superuser

```bash
docker compose exec api python src/manage.py migrate
docker compose exec api python src/manage.py createsuperuser
```

## 6. Data loading (optional)

If you need to seed catalogue data (cities, car marks), put fixtures under
`src/*/fixtures/` and run:

```bash
docker compose exec api python src/manage.py loaddata <fixture-name>
```

## 7. Cert renewal

Add a cron entry on the host:

```cron
0 4 * * * cd /opt/avtohelp && docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot renew && docker compose -f docker-compose.yml -f docker-compose.prod.yml exec nginx nginx -s reload
```

## 8. Logs

```bash
docker compose logs -f api          # gunicorn + django
docker compose logs -f ws           # daphne (WebSocket)
docker compose logs -f celery       # worker
docker compose logs -f celery-beat  # scheduler
docker compose logs -f nginx        # edge
```

## 9. Android client URL

The Android app hardcodes the base URL at build time. After this deploy is up,
rebuild the app with:

- `API_ENDPOINT="https://avtohelp24.ru/api/v1.0.0/"`
- WebSocket URL `wss://avtohelp24.ru/chat/stream`

See `roadhelpandroid/app/build.gradle` flavors.
