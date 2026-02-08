FROM python:3.12.10-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-ansi

COPY . .


FROM python:3.12.10-slim

ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    APP_USER=shipay \
    VENV_PATH=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
        curl && \
    rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash ${APP_USER}

WORKDIR ${APP_HOME}

COPY --from=builder /app/.venv ${VENV_PATH}

COPY --chown=${APP_USER}:${APP_USER} . .

USER ${APP_USER}

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/health/\?format\=json || exit 1

CMD ["sh", "-c", "python -m alembic upgrade head && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000"]
