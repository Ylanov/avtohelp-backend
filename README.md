# Introduction 

[![pipeline status](https://gitlab.com/Agencypro/roadhelpbackend/badges/dev/pipeline.svg)](https://gitlab.com/Agencypro/roadhelpbackend/-/commits/master)

[![coverage report](https://gitlab.com/Agencypro/roadhelpbackend/badges/master/coverage.svg)](https://gitlab.com/Agencypro/roadhelpbackend/-/commits/master)


This is backend application of the roadhelpbackend. 

# Development

## Environment

Requirements:
- Python 3.7
- Poetry
- Postgres 12
- Redis-server

# Introduction 

This is backend application of the roadhelpbackend-app. 

# Development
before start 


mac-os
```
brew install gdal
brew install docker-compose
```

Install docker for mac os -> [link](https://docs.docker.com/desktop/mac/install/) 

linux

```
sudo apt-get install gdal-bin
sudo apt-get install docker-compose docker

```

For both platforms

```
pip install poetry
poetry install
```

For added new dependency
```
poetry add <dependency-name>
```

For remove some dependency
```
poetry remove <dependency-name>
```

🏃‍For running django-app / django-api
```
make runserver (dev-server) (for unix-like OS)
make run-gunicorn (throw gunicorn)
```

For prepare dev-env
```
docker-compose -f docker-compose.local-db.yml up -d
```

## Admin url
```
Django-admin url http://127.0.0.1:8000/admin/

* login - +79000000000
* password - password
```

[Swagger-Docs](127.0.0.1:8000/swagger/)

## Environment

Requirements:
- Python 3.7
- Poetry
- Postgres 12

# Env-variable for running application

## Base settings
| Env-name      | Type | Default value|
| ----------- | ----------- | ----------- |
| DEBUG      | Title       |   True    |
| REDIS_URL   | Text        |  localhost     |
| REDIS_PORT   | Text        |  6379     |
| REDIS_DB   | Text        |   0    |
| DB_HOST   | Text        |   postgres (docker) or localhost    |
| DB_NAME   | Text        |       |
| DB_PORT   | Text        |       |
| DB_USER   | Text        |       |
| DB_PASSWORD   | Text        |       |
| TIME_ZONE   | Text        |       |
| USE_TZ   | bool        |       |
| USE_TZ   | bool        |       |
| USE_I18N   | bool        |       |
| USE_L10N   | bool        |       |
| USE_CELERY   | bool        |       |
| SECRET_KEY   | Text        |       |
| APPROVE_ACCOUNT   | Text        |       |
| TEST_SMS_CODE   | Text        |       |
| USE_SMS   | bool        |       |
| PAGE_SIZE   | Text        |       |
| SMS_SEND_DELAY   | Text        |       |
| SMS_CODE_LENGTH   | int        |       |
| SMS_INPUT_ATTEMPTS   | int        |       |
| SMS_BLOCKING_PERIOD   | int        |       |
| LIMIT_UNREAD_MESSAGES   | int        |       |
| MESSAGES_UPDATE_PERIOD   | int        |       |
| SESSION_SAVE_EVERY_REQUEST   | bool        |       |
| DATA_UPLOAD_MAX_MEMORY_SIZE   | int        |       |
| FILE_UPLOAD_PERMISSIONS   | Text        |       |
| NEWSLETTER_USERPROFILE_ID   | int        |       |
| NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS   | bool        |       |
| REQUEST_RELEVANCE   | Text        |       |
| DEFAULT_REQUEST_RADIUS   | int        |       |


##   3rd-party integrations
| Env-name      | Type | Default value|
| ----------- | ----------- | ----------- |
| SENTRY_DSN   | URL        |       |
| SMS_SERVICE   | URL        |       |
| SMS_LOGIN   | Text        |       |
| SMS_PASSWORD   | Text        |       |
| SMS_SENDER   | Text        |       |
| FCM_SERVER_KEY   | Text        |       |
| OTP_SERVICE   | Text        |       |
| OTP_SERVER_KEY   | Text        |       |
| OTP_SIGNATURE_KEY   | Text        |       |