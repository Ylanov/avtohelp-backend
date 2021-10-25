start: migrate collectstatic run-gunicorn

code-style: black flake8 isort

run-gunicorn:
	cd src/ && gunicorn --workers 4 --bind 0.0.0.0:8000 roadhelpbackend.wsgi:application

pytest:
	PYTHONPATH=./src pytest -q  --cov-report=

flake8:
	flake8 src/

pep8:
	pep8 --exclude='*/migrations/*,roadhelpbackend' --show-source --count src/

mypy:
	mypy --strict-optional --pretty src/

isort:
	python3 -m isort --filter-files src/

build:
	docker build -t registry.gitlab.com/agencypro/roadhelpbackend:python-3.7.2-based .
	docker push registry.gitlab.com/agencypro/roadhelpbackend:python-3.7.2-based

migrate:
	cd src/ && python3 manage.py migrate --noinput

collectstatic:
	cd src/ && python3 manage.py collectstatic --noinput

fixtures:
	cd src/ && python3 manage.py loaddata quize

makemigrations:
	cd src/ && python3 manage.py makemigrations

apply-migrations:
	cd src/ && python3 manage.py migrate

runserver:
	cd src/ && python3 manage.py runserver 0.0.0.0:8000

celery:
	cd src/ &&  celery -A roadhelpbackend worker -l INFO -E -n roadhelpbackend.%h

black:
	python3 -m black --line-length 79 src/

notebook:
	cd src/ && python3 manage.py shell_plus --notebook

dj-test:
	cd src/ && python3 manage.py test

release:
	ansible-playbook --inventory=deploy/inventory/prod deploy/roles/roadhelper.yml \
		--ssh-common-args='-o StrictHostKeyChecking=no' \
		-u root \
		-e "action='release'" \
		-e "roadhelpbackend_settings.DEBUG='${DEBUG}'" \
		-e "roadhelpbackend_settings.REDIS_URL='${REDIS_URL}'" \
		-e "roadhelpbackend_settings.REDIS_PORT='${REDIS_PORT}'" \
		-e "roadhelpbackend_settings.REDIS_DB='${REDIS_DB}'" \
		-e "roadhelpbackend_settings.DB_NAME='${DB_NAME}'" \
		-e "roadhelpbackend_settings.DB_USERNAME='${DB_USERNAME}'" \
		-e "roadhelpbackend_settings.DB_HOST='${DB_HOST}'" \
		-e "roadhelpbackend_settings.DB_PORT='${DB_PORT}'" \
		-e "roadhelpbackend_settings.DB_PASSWORD='${DB_PASSWORD}'" \
		-e "roadhelpbackend_settings.CELERY_BROKER_URL='${CELERY_BROKER_URL}'" \
		-e "roadhelpbackend_settings.TIME_ZONE='${TIME_ZONE}'" \
		-e "roadhelpbackend_settings.USE_TZ='${USE_TZ}'" \
		-e "roadhelpbackend_settings.USE_I18N='${USE_I18N}'" \
		-e "roadhelpbackend_settings.USE_L10N='${USE_L10N}'" \
		-e "roadhelpbackend_settings.USE_CELERY='${USE_CELERY}'" \
		-e "roadhelpbackend_settings.SECRET_KEY='${SECRET_KEY}'" \
		-e "roadhelpbackend_settings.SENTRY_DSN='${SENTRY_DSN}'" \
		-e "roadhelpbackend_settings.SMS_SERVICE='${SMS_SERVICE}'" \
		-e "roadhelpbackend_settings.SMS_PASSWORD='${SMS_PASSWORD}'" \
		-e "roadhelpbackend_settings.SMS_SENDER='${SMS_SENDER}'" \
		-e "roadhelpbackend_settings.APPROVE_ACCOUNT='${APPROVE_ACCOUNT}'" \
		-e "roadhelpbackend_settings.TEST_SMS_CODE='${TEST_SMS_CODE}'" \
		-e "roadhelpbackend_settings.USE_SMS='${USE_SMS}'" \
		-e "roadhelpbackend_settings.PAGE_SIZE='${PAGE_SIZE}'" \
		-e "roadhelpbackend_settings.SMS_SEND_DELAY='${SMS_SEND_DELAY}'" \
		-e "roadhelpbackend_settings.SMS_CODE_LENGTH='${SMS_CODE_LENGTH}'" \
		-e "roadhelpbackend_settings.SMS_INPUT_ATTEMPTS='${SMS_INPUT_ATTEMPTS}'" \
		-e "roadhelpbackend_settings.SMS_BLOCKING_PERIOD='${SMS_BLOCKING_PERIOD}'" \
		-e "roadhelpbackend_settings.NEWSLETTER_USERPROFILE_ID='${NEWSLETTER_USERPROFILE_ID}'" \
		-e "roadhelpbackend_settings.NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS='${NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS}'" \
		-e "roadhelpbackend_settings.REQUEST_RELEVANCE='${REQUEST_RELEVANCE}'" \
		-e "roadhelpbackend_settings.DEFAULT_REQUEST_RADIUS='${DEFAULT_REQUEST_RADIUS}'" \
		-e "roadhelpbackend_settings.FCM_SERVER_KEY='${FCM_SERVER_KEY}'" \
		-e "roadhelpbackend_settings.OTP_SERVICE='${OTP_SERVICE}'" \
		-e "roadhelpbackend_settings.OTP_SERVER_KEY='${OTP_SERVER_KEY}'" \
		-e "roadhelpbackend_settings.OTP_SIGNATURE_KEY='${OTP_SIGNATURE_KEY}'" \
		-e "roadhelpbackend_settings.LIMIT_UNREAD_MESSAGES='${LIMIT_UNREAD_MESSAGES}'" \
		-e "roadhelpbackend_settings.MESSAGES_UPDATE_PERIOD='${MESSAGES_UPDATE_PERIOD}'" \
		-e "roadhelpbackend_settings.SESSION_SAVE_EVERY_REQUEST='${SESSION_SAVE_EVERY_REQUEST}'" \
		-e "roadhelpbackend_settings.DATA_UPLOAD_MAX_MEMORY_SIZE='${DATA_UPLOAD_MAX_MEMORY_SIZE}'" \
		-e "roadhelpbackend_settings.FILE_UPLOAD_PERMISSIONS='${FILE_UPLOAD_PERMISSIONS}'" \
