from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, instance: Any, *, refresh: bool = False) -> Any:
        self.session.add(instance)
        await self.session.flush()
        if refresh:
            await self.session.refresh(instance)
        return instance

    async def delete(self, instance: Any) -> None:
        await self.session.delete(instance)
        await self.session.flush()

    async def commit(self) -> None:
        if self.session.in_transaction():
            await self.session.commit()

    async def rollback(self) -> None:
        if self.session.in_transaction():
            await self.session.rollback()

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator["BaseRepository"]:
        try:
            yield self
            await self.commit()
        except Exception:
            await self.rollback()
            raise

    async def refresh(self, instance: Any) -> None:
        await self.session.refresh(instance)
