from collections.abc import AsyncIterator

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.presentation import deps


@pytest.fixture
async def e2e_client(
    postgres_prepared_session: AsyncSession,
) -> AsyncIterator[tuple[httpx.AsyncClient, AsyncSession]]:
    session = postgres_prepared_session

    async def _override_get_db():
        try:
            yield session
        finally:
            if session.in_transaction():
                await session.rollback()

    original_overrides = dict(app.dependency_overrides)
    app.dependency_overrides[deps.get_db] = _override_get_db
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)

    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            yield client, session
    finally:
        app.dependency_overrides = original_overrides
