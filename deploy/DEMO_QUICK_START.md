# Demo deploy — 153.80.245.74

Fast path to get RoadHelp running on the production cloud server so the
existing Android `bug_fix` build (hardcoded to `http://153.80.245.74:8000/`)
talks to it without a rebuild.

Two phases:
- **Phase 1 — HTTP on :8000** (today). Android works immediately.
- **Phase 2 — HTTPS via avtohelp24.ru** (before the investor demo). Requires
  an Android rebuild pointing to `https://avtohelp24.ru/api/v1.0.0/`.

---

## Phase 1 — HTTP on :8000

### 1. SSH to the server

```bash
ssh <you>@153.80.245.74
```

### 2. Install Docker (Ubuntu 22.04+)

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg git
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
     https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"
# re-login so the group takes effect
```

### 3. Open ports 80, 443, 8000

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp     # for Phase 1, Android talks here
sudo ufw enable
```

If the cloud provider has its own firewall/security group, open the same
three ports there too.

### 4. Clone the repo on the modernised branch

```bash
sudo mkdir -p /opt/avtohelp && sudo chown $USER /opt/avtohelp
cd /opt/avtohelp
git clone https://github.com/<your-org>/roadhelpbackend.git .
git checkout claude/vigorous-tereshkova-c18f3e
```

If the repo isn't pushed yet, push it first from your laptop:

```powershell
cd C:\Users\yrosh\PycharmProjects\roadhelpbackend
git push origin claude/vigorous-tereshkova-c18f3e
```

### 5. Fill `.env` with real secrets

```bash
cp .env.example .env
$EDITOR .env
```

Minimum to get a live demo:

```env
SECRET_KEY=<generate with: python3 -c "import secrets; print(secrets.token_urlsafe(64))">
DEBUG=false
ALLOWED_HOSTS=153.80.245.74,avtohelp24.ru,localhost
DJANGO_SETTINGS_MODULE=roadhelpbackend.settings.prod
DB_NAME=roadhelp
DB_USER=roadhelp
DB_PASSWORD=<strong random>
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis
REDIS_PORT=6379
REDIS_DB=0
TIME_ZONE=Europe/Moscow
USE_TZ=true
USE_I18N=true
USE_CELERY=true

# Fast demo shortcut: any +79… phone will accept code "12345".
# Flip to false once real SMSC credentials are filled in.
TEST_SMS_CODE=true
USE_SMS=false
APPROVE_ACCOUNT=

# SMS (SMSC.ru) — fill before TEST_SMS_CODE=false
SMS_LOGIN=
SMS_PASSWORD=
SMS_SENDER=RoadHelper

# OTP voice fallback (new-tel.net) — optional
OTP_SERVER_KEY=
OTP_SIGNATURE_KEY=

# FCM push — put the Firebase service-account JSON at ./secrets/fcm-service-account.json
GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/fcm-service-account.json

SENTRY_DSN=
```

Put the Firebase key:

```bash
mkdir -p ./secrets
# upload fcm-service-account.json to ./secrets/ via scp
chmod 600 ./secrets/fcm-service-account.json
```

### 6. Bring up the stack

```bash
docker compose up -d --build
```

First build takes ~3 min (Poetry lock + deps). Subsequent rebuilds cache.

### 7. Check it's alive

```bash
docker compose ps                     # all 6 services running
curl http://127.0.0.1:8000/health/    # {"status":"ok"}
docker compose logs -f api            # Ctrl-C to stop tailing
```

From your laptop:

```powershell
curl http://153.80.245.74:8000/health/
```

### 8. Seed demo data

```bash
docker compose exec api python src/manage.py seed_demo
docker compose exec api python src/manage.py createsuperuser
```

`seed_demo` loads:
- 15 Russian cities (Moscow, SPB, etc.)
- 12 car brands × 5 models each (Lada, Toyota, Kia, BMW, …)
- 15 common car colours

### 9. Smoke from Android

Open the `bug_fix` build of the Android app. Do a full flow:

1. Enter any Russian phone (e.g. `+79991234567`) → request code
2. Enter `12345` → should receive token + profile
3. Add a car (the seeded brands/models should show up)
4. Create an assistance request with a location

If something 500s — check `docker compose logs api` on the server.

---

## Phase 2 — HTTPS via avtohelp24.ru (before the investor demo)

### 1. Point DNS
At your registrar, set:

```
A     avtohelp24.ru     153.80.245.74
A     www.avtohelp24.ru 153.80.245.74
```

Wait for propagation (`dig avtohelp24.ru` should show the IP).

### 2. Issue the Let's Encrypt cert

```bash
cd /opt/avtohelp
# Start nginx + certbot from the prod overlay
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d nginx

# Obtain the cert (webroot challenge)
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot \
    certonly --webroot -w /var/www/certbot \
    -d avtohelp24.ru -d www.avtohelp24.ru \
    --email <you@example.com> --agree-tos --no-eff-email

# Reload nginx with the new cert
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart nginx
```

Test: `curl https://avtohelp24.ru/health/` → `{"status": "ok"}`.

### 3. Rebuild Android with the new base URL

In `roadhelpandroid/app/build.gradle`, update each flavor:

```gradle
buildConfigField "String", "API_ENDPOINT", "\"https://avtohelp24.ru/api/v1.0.0/\""
buildConfigField "String", "WS_URL",       "\"wss://avtohelp24.ru/chat/stream\""
```

Rebuild the APK, install, retest the full flow on HTTPS.

### 4. Automate renewal

```bash
sudo crontab -e
# every day at 04:00 try to renew; no-op if still valid
0 4 * * * cd /opt/avtohelp && docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot renew && docker compose -f docker-compose.yml -f docker-compose.prod.yml exec nginx nginx -s reload
```

---

## Useful one-liners

```bash
# Tail all services
docker compose logs -f

# Apply a migration after a git pull
git pull && docker compose exec api python src/manage.py migrate

# Run contract tests on the server (requires INSTALL_DEV=true image)
docker compose exec api python -m pytest -m contract

# Django shell
docker compose exec api python src/manage.py shell

# Backup db
docker compose exec db pg_dump -U roadhelp roadhelp > backup-$(date +%F).sql
```
