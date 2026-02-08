from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager


class UnitOfWorkPort(ABC):
    @abstractmethod
    def transaction(self) -> AbstractAsyncContextManager[None]:
        """Provide a transaction boundary for application use cases."""
