from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence import models  # noqa: F401
from src.main import app


@pytest.fixture
def api_client():
    original_overrides = dict(app.dependency_overrides)

    @asynccontextmanager
    async def _client_factory(overrides: dict | None = None):
        overrides = overrides or {}
        previous_overrides = dict(app.dependency_overrides)
        app.dependency_overrides.update(overrides)
        transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
        try:
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                yield client
        finally:
            app.dependency_overrides = previous_overrides

    try:
        yield _client_factory
    finally:
        app.dependency_overrides = original_overrides


@pytest.fixture
async def repo_session(
    postgres_prepared_session: AsyncSession,
) -> AsyncIterator[AsyncSession]:
    yield postgres_prepared_session
