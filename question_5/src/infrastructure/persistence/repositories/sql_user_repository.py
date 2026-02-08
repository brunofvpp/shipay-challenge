from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import exists

from src.domain.entities import UserEntity
from src.domain.repositories import UserRepositoryPort
from src.infrastructure.persistence.models import User
from src.infrastructure.persistence.repositories.base import BaseRepository


class SqlUserRepository(BaseRepository, UserRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def exists_by_email(self, email: str) -> bool:
        query = select(exists().where(User.email == email))
        result = await self.session.scalar(query)
        return bool(result)

    async def create(
        self,
        *,
        name: str,
        email: str,
        password: str,
        role_id: int,
    ) -> UserEntity:
        user = User(
            name=name,
            email=email,
            password=password,
            role_id=role_id,
            created_at=date.today(),
            updated_at=None,
        )
        return await self.save(user)
