from abc import abstractmethod

from src.domain.entities import UserEntity
from src.domain.repositories.repository_port import RepositoryPort


class UserRepositoryPort(RepositoryPort[UserEntity]):
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if email is already in use."""

    @abstractmethod
    async def create(
        self,
        *,
        name: str,
        email: str,
        password: str,
        role_id: int,
    ) -> UserEntity:
        """Create a new user record."""
