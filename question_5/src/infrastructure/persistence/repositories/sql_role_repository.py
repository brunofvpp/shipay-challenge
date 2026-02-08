from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import RoleEntity
from src.domain.repositories import RoleRepositoryPort
from src.infrastructure.persistence.models import Role
from src.infrastructure.persistence.repositories.base import BaseRepository


class SqlRoleRepository(BaseRepository, RoleRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, role_id: int) -> RoleEntity | None:
        query = select(Role).where(Role.id == role_id)
        return await self.session.scalar(query)
