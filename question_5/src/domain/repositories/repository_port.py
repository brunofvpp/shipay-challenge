from abc import ABC, abstractmethod
from typing import Generic, TypeVar

EntityT = TypeVar("EntityT")


class RepositoryPort(ABC, Generic[EntityT]):
    @abstractmethod
    async def save(self, instance: EntityT) -> EntityT:
        """Persist an entity instance."""

    @abstractmethod
    async def refresh(self, instance: EntityT) -> None:
        """Refresh an entity instance from persistence."""
