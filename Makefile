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
