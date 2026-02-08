from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable

import pytest
from sqlalchemy import Integer, String, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.infrastructure.persistence.repositories.base import BaseRepository


class Base(DeclarativeBase):
    pass


class Widget(Base):
    __tablename__ = "widgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


class WidgetRepository(BaseRepository):
    async def create(self, name: str) -> Widget:
        widget = Widget(name=name)
        return await self.save(widget, refresh=True)


@pytest.fixture
async def session_factory(
    postgres_async_engine,
    postgres_test_schema: str,
) -> AsyncIterator[Callable[[], AsyncIterator[AsyncSession]]]:
    async with postgres_async_engine.begin() as conn:
        await conn.execute(text(f'SET search_path TO "{postgres_test_schema}"'))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(postgres_async_engine, class_=AsyncSession, expire_on_commit=False)

    @asynccontextmanager
    async def _factory() -> AsyncIterator[AsyncSession]:
        async with factory() as session:
            await session.execute(text(f'SET search_path TO "{postgres_test_schema}"'))
            yield session

    def _session_factory():
        return _factory()

    try:
        yield _session_factory
    finally:
        async with postgres_async_engine.begin() as conn:
            await conn.execute(text(f'SET search_path TO "{postgres_test_schema}"'))
            await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.anyio
async def test_transaction_commit_persists_widget(session_factory):
    # Arrange
    async with session_factory() as session:
        repo = WidgetRepository(session)
        # Act
        async with repo.transaction():
            await repo.create("Widget A")
    # Assert
    async with session_factory() as verify_session:
        result = await verify_session.execute(select(Widget))
        widgets = result.scalars().all()
        assert [w.name for w in widgets] == ["Widget A"]


@pytest.mark.anyio
async def test_transaction_rollback_discards_widget_on_exception(session_factory):
    # Arrange
    async with session_factory() as session:
        repo = WidgetRepository(session)
        # Act
        with pytest.raises(RuntimeError):
            async with repo.transaction():
                await repo.create("Widget B")
                raise RuntimeError("boom")
    # Assert
    async with session_factory() as verify_session:
        result = await verify_session.execute(select(Widget))
        assert result.scalars().all() == []


@pytest.mark.anyio
async def test_delete_removes_widget_from_database(session_factory):
    # Arrange
    async with session_factory() as setup_session:
        setup_repo = WidgetRepository(setup_session)
        async with setup_repo.transaction():
            await setup_repo.create("Widget C")
    # Act
    async with session_factory() as session:
        repo = WidgetRepository(session)
        widget = (await session.execute(select(Widget))).scalars().one()
        async with repo.transaction():
            await repo.delete(widget)
    # Assert
    async with session_factory() as verify_session:
        result = await verify_session.execute(select(Widget))
        assert result.scalars().all() == []
