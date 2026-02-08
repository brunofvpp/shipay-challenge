from abc import ABC, abstractmethod

from src.domain.entities import RoleEntity


class RoleRepositoryPort(ABC):
    @abstractmethod
    async def get_by_id(self, role_id: int) -> RoleEntity | None:
        """Retrieve a role by id."""
