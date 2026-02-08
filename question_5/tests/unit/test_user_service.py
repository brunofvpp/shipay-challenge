from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import date
from typing import Any

import pytest

from src.application.exceptions import EmailAlreadyExistsError, RoleNotFoundError
from src.application.schemas import UserCreateInput, UserOutput
from src.application.use_cases.create_user import CreateUserUseCase
from src.domain.entities import RoleEntity
from src.infrastructure.persistence.models import User


@dataclass
class FakeRoleRepository:
    roles: dict[int, Any] = field(default_factory=dict)

    async def get_by_id(self, role_id: int) -> Any | None:
        return self.roles.get(role_id)


@dataclass
class FakeUserRepository:
    existing_emails: set[str] = field(default_factory=set)
    created_users: list[Any] = field(default_factory=list)
    last_password: str | None = None
    refreshed: list[Any] = field(default_factory=list)

    async def exists_by_email(self, email: str) -> bool:
        return email in self.existing_emails

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
        self.last_password = password
        return user

    async def refresh(self, instance: Any) -> None:
        self.refreshed.append(instance)


@dataclass
class FakeUnitOfWork:
    transaction_committed: bool = False
    transaction_rolled_back: bool = False

    @asynccontextmanager
    async def transaction(self):
        try:
            yield
            self.transaction_committed = True
        except Exception:
            self.transaction_rolled_back = True
            raise


@pytest.mark.anyio
async def test_create_user_hashes_provided_password_and_persists_user():
    # Arrange
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository({1: RoleEntity(id=1, description="Admin")})
    unit_of_work = FakeUnitOfWork()
    service = CreateUserUseCase(user_repo, role_repo, unit_of_work)
    payload = UserCreateInput(name="Bruno", email="bruno@fagundes.com", role_id=1, password="Plain123!")
    # Act
    result: UserOutput = await service.create_user(payload)
    # Assert
    assert result.email == payload.email
    assert len(user_repo.created_users) == 1
    assert user_repo.last_password != payload.password


@pytest.mark.anyio
async def test_create_user_generates_password_when_not_supplied(monkeypatch):
    # Arrange
    generated_password = "TempPass1!"
    monkeypatch.setattr("src.application.use_cases.create_user.generate_password", lambda length=8: generated_password)
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository({1: RoleEntity(id=1, description="Admin")})
    unit_of_work = FakeUnitOfWork()
    service = CreateUserUseCase(user_repo, role_repo, unit_of_work)
    payload = UserCreateInput(name="Ana", email="ana@fagundes.com", role_id=1, password=None)
    # Act
    result = await service.create_user(payload)
    # Assert
    assert result.email == payload.email
    assert user_repo.last_password is not None
    assert generated_password not in user_repo.last_password


@pytest.mark.anyio
async def test_create_user_raises_role_not_found_when_role_missing():
    # Arrange
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository()
    service = CreateUserUseCase(user_repo, role_repo, FakeUnitOfWork())
    payload = UserCreateInput(name="NoRole", email="norole@fagundes.com", role_id=999, password="Plain123!")
    # Act & Assert
    with pytest.raises(RoleNotFoundError):
        await service.create_user(payload)


@pytest.mark.anyio
async def test_create_user_raises_email_conflict_when_email_exists():
    # Arrange
    user_repo = FakeUserRepository(existing_emails={"taken@fagundes.com"})
    role_repo = FakeRoleRepository({1: RoleEntity(id=1, description="Admin")})
    service = CreateUserUseCase(user_repo, role_repo, FakeUnitOfWork())
    payload = UserCreateInput(name="Taken", email="taken@fagundes.com", role_id=1, password="Plain123!")
    # Act & Assert
    with pytest.raises(EmailAlreadyExistsError):
        await service.create_user(payload)


@pytest.mark.anyio
async def test_create_user_commits_and_refreshes_when_creation_succeeds():
    # Arrange
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository({1: RoleEntity(id=1, description="Admin")})
    unit_of_work = FakeUnitOfWork()
    service = CreateUserUseCase(user_repo, role_repo, unit_of_work)
    payload = UserCreateInput(name="Commit", email="commit@fagundes.com", role_id=1, password="Plain123!")
    # Act
    result = await service.create_user(payload)
    # Assert
    assert unit_of_work.transaction_committed is True
    assert unit_of_work.transaction_rolled_back is False
    assert user_repo.refreshed == [user_repo.created_users[0]]
    assert result.email == payload.email


@pytest.mark.anyio
async def test_create_user_rolls_back_when_repository_raises(monkeypatch):
    # Arrange
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository({1: RoleEntity(id=1, description="Admin")})
    unit_of_work = FakeUnitOfWork()
    service = CreateUserUseCase(user_repo, role_repo, unit_of_work)
    payload = UserCreateInput(name="Rollback", email="rollback@fagundes.com", role_id=1, password="Plain123!")

    async def failing_create(**kwargs):
        raise RuntimeError("db error")

    monkeypatch.setattr(user_repo, "create", failing_create)
    # Act & Assert
    with pytest.raises(RuntimeError):
        await service.create_user(payload)
    assert unit_of_work.transaction_committed is False
    assert unit_of_work.transaction_rolled_back is True
