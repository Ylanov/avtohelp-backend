start: migrate collectstatic

code-style: black flake8 isort pep8

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
	docker build -t super-service:latest .

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
black:
	python3 -m black src/

notebook:
	cd src/ && python3 manage.py shell_plus --notebook
