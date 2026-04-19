# Convenience targets. Docker compose does the heavy lifting.
.PHONY: up down build migrate makemigrations createsuperuser shell logs pytest test contract lint format check

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

migrate:
	docker compose exec api python src/manage.py migrate --noinput

makemigrations:
	docker compose exec api python src/manage.py makemigrations

createsuperuser:
	docker compose exec api python src/manage.py createsuperuser

shell:
	docker compose exec api python src/manage.py shell_plus || \
	docker compose exec api python src/manage.py shell

logs:
	docker compose logs -f api ws celery celery-beat

pytest:
	docker compose exec api pytest

contract:
	docker compose exec api pytest -m contract

check:
	docker compose exec api python src/manage.py check --deploy

lint:
	docker compose exec api ruff check src/

format:
	docker compose exec api ruff format src/

test: contract
