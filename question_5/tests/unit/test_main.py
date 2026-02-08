import os

import httpx
import pytest

from src.application.exceptions import RFC7807Exception
from src.main import create_application

DEFAULT_ENV = {
    "DATABASE_HOST": "localhost",
    "DATABASE_PORT": "5432",
    "DATABASE_USER": "test",
    "DATABASE_PASS": "test",
    "DATABASE_SCHEMA": "test_db",
}

for key, value in DEFAULT_ENV.items():
    os.environ.setdefault(key, value)


async def _make_client(app):
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.anyio
async def test_rfc7807_handler_returns_problem_response():
    # Arrange
    app = create_application()

    @app.get("/problem")
    async def problem():
        raise RFC7807Exception(status_code=418, kind="custom-problem", title="Nope", detail="It broke")

    # Act
    client = await _make_client(app)
    try:
        response = await client.get("/problem")
    finally:
        await client.aclose()

    # Assert
    assert response.status_code == 418
    body = response.json()
    assert body["type"] == "custom-problem"
    assert body["title"] == "Nope"
    assert body["detail"] == "It broke"


@pytest.mark.anyio
async def test_generic_handler_returns_internal_error_payload():
    # Arrange
    app = create_application()

    @app.get("/boom")
    async def boom():
        raise RuntimeError("kaboom")

    # Act
    client = await _make_client(app)
    try:
        response = await client.get("/boom")
    finally:
        await client.aclose()

    # Assert
    assert response.status_code == 500
    payload = response.json()
    assert payload["type"] == "internal-server-error"
    assert payload["title"] == "Internal server error"


@pytest.mark.anyio
async def test_root_redirects_to_docs():
    # Arrange
    app = create_application()

    # Act
    client = await _make_client(app)
    try:
        response = await client.get("/", follow_redirects=False)
    finally:
        await client.aclose()

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"
