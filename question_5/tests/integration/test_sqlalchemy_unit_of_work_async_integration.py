import pytest
from sqlalchemy import Integer, String, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork


class Base(DeclarativeBase):
    pass


class Widget(Base):
    __tablename__ = "widgets_async"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


@pytest.fixture
async def async_session_factory(postgres_async_engine, postgres_test_schema: str):
    async with postgres_async_engine.begin() as conn:
        await conn.execute(text(f'SET search_path TO "{postgres_test_schema}"'))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(postgres_async_engine, expire_on_commit=False, class_=AsyncSession)
    try:
        yield session_factory
    finally:
        async with postgres_async_engine.begin() as conn:
            await conn.execute(text(f'SET search_path TO "{postgres_test_schema}"'))
            await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.anyio
async def test_uow_commits_with_real_async_session(async_session_factory):
    # Arrange
    async with async_session_factory() as session:
        uow = SqlAlchemyUnitOfWork(session)

        # Act
        async with uow.transaction():
            session.add(Widget(name="committed"))
            await session.flush()

    # Assert
    async with async_session_factory() as verify_session:
        result = await verify_session.execute(select(Widget))
        assert [row.name for row in result.scalars().all()] == ["committed"]


@pytest.mark.anyio
async def test_uow_rolls_back_with_real_async_session(async_session_factory):
    # Arrange
    async with async_session_factory() as session:
        uow = SqlAlchemyUnitOfWork(session)

        # Act
        with pytest.raises(RuntimeError, match="boom"):
            async with uow.transaction():
                session.add(Widget(name="rolled-back"))
                await session.flush()
                raise RuntimeError("boom")

    # Assert
    async with async_session_factory() as verify_session:
        result = await verify_session.execute(select(Widget))
        assert result.scalars().all() == []
