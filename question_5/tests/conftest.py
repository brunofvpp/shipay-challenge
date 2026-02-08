import asyncio
import os
import sys
import uuid
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from src.infrastructure.persistence import models  # noqa: F401

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


TRUNCATE_CORE_TABLES_SQL = text("TRUNCATE TABLE user_claims, users, claims, roles RESTART IDENTITY CASCADE")


def _required_env(key: str) -> str:
    value = os.getenv(key)
    if value:
        return value
    raise RuntimeError(f"Missing required environment variable: {key}")


def _database_env() -> dict[str, str]:
    return {
        "host": _required_env("DATABASE_HOST"),
        "port": _required_env("DATABASE_PORT"),
        "user": _required_env("DATABASE_USER"),
        "password": _required_env("DATABASE_PASS"),
    }


def _test_database_name() -> str:
    return f"{_required_env('DATABASE_SCHEMA')}_test"


@pytest.fixture(scope="session")
def postgres_test_schema() -> Iterator[str]:
    db_env = _database_env()
    database_name = _test_database_name()
    schema_name = f"test_{uuid.uuid4().hex}"

    admin_sync_url = (
        f"postgresql+psycopg2://{db_env['user']}:{db_env['password']}"
        f"@{db_env['host']}:{db_env['port']}/postgres"
        "?connect_timeout=3"
    )
    admin_engine = create_engine(admin_sync_url, future=True, isolation_level="AUTOCOMMIT")
    with admin_engine.begin() as conn:
        exists = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": database_name})
        if exists.scalar() is None:
            conn.execute(text(f'CREATE DATABASE "{database_name}"'))
    admin_engine.dispose()

    sync_url = (
        f"postgresql+psycopg2://{db_env['user']}:{db_env['password']}"
        f"@{db_env['host']}:{db_env['port']}/{database_name}"
        "?connect_timeout=3"
    )
    engine = create_engine(sync_url, future=True)
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA "{schema_name}"'))
        conn.execute(text(f'SET search_path TO "{schema_name}"'))
        SQLModel.metadata.create_all(bind=conn)
    try:
        yield schema_name
    finally:
        with engine.begin() as conn:
            conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))
        engine.dispose()


@pytest.fixture(scope="session")
def postgres_async_engine(postgres_test_schema: str) -> Iterator[AsyncEngine]:
    db_env = _database_env()
    database_name = _test_database_name()
    async_url = (
        f"postgresql+asyncpg://{db_env['user']}:{db_env['password']}@{db_env['host']}:{db_env['port']}/{database_name}"
    )
    engine = create_async_engine(
        async_url,
        connect_args={
            "timeout": 3,
            "command_timeout": 5,
            "server_settings": {"search_path": postgres_test_schema},
        },
        pool_pre_ping=True,
        poolclass=NullPool,
    )
    yield engine
    asyncio.run(engine.dispose())


@pytest.fixture(scope="session")
def postgres_async_session_factory(
    postgres_async_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(postgres_async_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def postgres_prepared_session(
    postgres_async_session_factory: async_sessionmaker[AsyncSession],
    postgres_test_schema: str,
) -> AsyncIterator[AsyncSession]:
    session = postgres_async_session_factory()
    await session.execute(text(f'SET search_path TO "{postgres_test_schema}"'))
    await session.execute(TRUNCATE_CORE_TABLES_SQL)
    await session.commit()
    try:
        yield session
    finally:
        if session.in_transaction():
            await session.rollback()
        await session.close()
