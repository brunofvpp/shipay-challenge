from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain import UnitOfWorkPort


class SqlAlchemyUnitOfWork(UnitOfWorkPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        try:
            yield
            if self.session.in_transaction():
                await self.session.commit()
        except Exception:
            if self.session.in_transaction():
                await self.session.rollback()
            raise
