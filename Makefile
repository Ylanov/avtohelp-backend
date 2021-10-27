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
	docker build -t registry.gitlab.com/agencypro/roadhelpbackend:python-3.7.2-based . -f Dockerfile.based
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
		-u gitlab-runner \
		-e "action='release'" \
		-e "DEBUG='${DEBUG}'" \
		-e "REDIS_URL='${REDIS_URL}'" \
		-e "REDIS_PORT=${REDIS_PORT}" \
		-e "REDIS_DB=${REDIS_DB}" \
		-e "DB_NAME='${DB_NAME}'" \
		-e "DB_USERNAME='${DB_USERNAME}'" \
		-e "DB_HOST='${DB_HOST}'" \
		-e "DB_PORT=${DB_PORT}" \
		-e "DB_PASSWORD='${DB_PASSWORD}'" \
		-e "CELERY_BROKER_URL='${CELERY_BROKER_URL}'" \
		-e "TIME_ZONE='${TIME_ZONE}'" \
		-e "USE_TZ='${USE_TZ}'" \
		-e "USE_I18N='${USE_I18N}'" \
		-e "USE_L10N='${USE_L10N}'" \
		-e "USE_CELERY='${USE_CELERY}'" \
		-e "SECRET_KEY='${SECRET_KEY}'" \
		-e "SENTRY_DSN='${SENTRY_DSN}'" \
		-e "SMS_SERVICE='${SMS_SERVICE}'" \
		-e "SMS_PASSWORD='${SMS_PASSWORD}'" \
		-e "SMS_SENDER='${SMS_SENDER}'" \
		-e "APPROVE_ACCOUNT='${APPROVE_ACCOUNT}'" \
		-e "TEST_SMS_CODE='${TEST_SMS_CODE}'" \
		-e "USE_SMS='${USE_SMS}'" \
		-e "PAGE_SIZE=${PAGE_SIZE}" \
		-e "SMS_SEND_DELAY=${SMS_SEND_DELAY}" \
		-e "SMS_CODE_LENGTH=${SMS_CODE_LENGTH}" \
		-e "SMS_INPUT_ATTEMPTS=${SMS_INPUT_ATTEMPTS}" \
		-e "SMS_BLOCKING_PERIOD=${SMS_BLOCKING_PERIOD}" \
		-e "NEWSLETTER_USERPROFILE_ID=${NEWSLETTER_USERPROFILE_ID}" \
		-e "NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS='${NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS}'" \
		-e "REQUEST_RELEVANCE='${REQUEST_RELEVANCE}'" \
		-e "DEFAULT_REQUEST_RADIUS=${DEFAULT_REQUEST_RADIUS}" \
		-e "FCM_SERVER_KEY='${FCM_SERVER_KEY}'" \
		-e "OTP_SERVICE='${OTP_SERVICE}'" \
		-e "OTP_SERVER_KEY='${OTP_SERVER_KEY}'" \
		-e "OTP_SIGNATURE_KEY='${OTP_SIGNATURE_KEY}'" \
		-e "LIMIT_UNREAD_MESSAGES='${LIMIT_UNREAD_MESSAGES}'" \
		-e "MESSAGES_UPDATE_PERIOD=${MESSAGES_UPDATE_PERIOD}" \
		-e "SESSION_SAVE_EVERY_REQUEST='${SESSION_SAVE_EVERY_REQUEST}'" \
		-e "DATA_UPLOAD_MAX_MEMORY_SIZE=${DATA_UPLOAD_MAX_MEMORY_SIZE}" \
		-e "FILE_UPLOAD_PERMISSIONS='${FILE_UPLOAD_PERMISSIONS}'"
