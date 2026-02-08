import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import date
from typing import Any

import pytest

from src.application.schemas import UserCreateInput
from src.application.use_cases.create_user import CreateUserUseCase
from src.domain.entities import RoleEntity
from src.infrastructure.persistence.models import User


@dataclass
class FakeRoleRepository:
    role: RoleEntity

    async def get_by_id(self, role_id: int) -> RoleEntity | None:
        if self.role.id == role_id:
            return self.role
        return None


@dataclass
class FakeConcurrentUserRepository:
    existing_emails: set[str] = field(default_factory=set)
    created_users: list[User] = field(default_factory=list)
    _exists_calls: int = 0

    def __post_init__(self) -> None:
        self._barrier = asyncio.Event()

    async def exists_by_email(self, email: str) -> bool:
        exists_snapshot = email in self.existing_emails
        self._exists_calls += 1
        if self._exists_calls == 2:
            self._barrier.set()
        await self._barrier.wait()
        return exists_snapshot

    async def create(self, *, name: str, email: str, password: str, role_id: int) -> Any:
        user = User(
            id=len(self.created_users) + 1,
            name=name,
            email=email,
            role_id=role_id,
            created_at=date.today(),
            updated_at=None,
            password=password,
        )
        self.created_users.append(user)
        self.existing_emails.add(email)
        return user

    async def refresh(self, instance: Any) -> None:
        return None


class FakeUnitOfWork:
    @asynccontextmanager
    async def transaction(self):
        yield


@pytest.mark.anyio
async def test_create_user_allows_duplicate_email_under_race_condition():
    # Arrange
    user_repository = FakeConcurrentUserRepository()
    role_repository = FakeRoleRepository(role=RoleEntity(id=1, description="Admin"))
    use_case = CreateUserUseCase(user_repository, role_repository, FakeUnitOfWork())
    payload = UserCreateInput(name="Race", email="race@example.com", role_id=1, password="Plain123!")

    async def _run_once():
        return await use_case.create_user(payload)

    # Act
    result_one, result_two = await asyncio.gather(_run_once(), _run_once())

    # Assert
    assert result_one.email == payload.email
    assert result_two.email == payload.email
    assert len(user_repository.created_users) == 2
