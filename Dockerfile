# syntax=docker/dockerfile:1.7
# Multi-stage: builder installs deps, runtime is slim.
# Build argument INSTALL_DEV=true pulls in the dev group (pytest etc.) — used
# by the local docker compose so `docker compose exec api pytest` Just Works.
# Prod/CI images should leave it at the false default.
FROM python:3.12-slim-bookworm AS builder

ARG INSTALL_DEV=false

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.8.5 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Build-time deps for psycopg[binary] wheel, GDAL headers for djangorestframework-gis,
# gettext for compilemessages.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libgdal-dev \
        gdal-bin \
        binutils \
        libproj-dev \
        libgeos-dev \
        gettext \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app
COPY pyproject.toml ./
# Lock is generated in the image — reproducibility handled via exact version pins
# in pyproject.toml rather than a committed lockfile (see README).
# When INSTALL_DEV=true the dev group is included so pytest / factory-boy /
# mypy / ruff all ship inside the image.
RUN poetry lock && \
    if [ "$INSTALL_DEV" = "true" ]; then \
        poetry install --with dev --no-root ; \
    else \
        poetry install --only main --no-root ; \
    fi


FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=roadhelpbackend.settings.prod \
    PYTHONPATH=/app/src

# Runtime libs only (no -dev packages, no build-essential).
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        libgdal32 \
        gdal-bin \
        libproj25 \
        libgeos-c1v5 \
        gettext \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app

# Non-root user for runtime
RUN groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app \
    && mkdir -p /app/media /app/static \
    && chown -R app:app /app

COPY --chown=app:app src /app/src/
COPY --chown=app:app locale /app/locale/
COPY --chown=app:app templates /app/templates/

USER app

EXPOSE 8000

# Healthcheck hits the /health/ endpoint defined in urls.
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://localhost:8000/health/ || exit 1

# Default command: gunicorn (WSGI for REST). Daphne runs in a separate service for WS.
CMD ["gunicorn", "--chdir", "/app/src", \
     "--workers", "4", \
     "--worker-class", "gthread", \
     "--threads", "2", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "roadhelpbackend.wsgi:application"]
