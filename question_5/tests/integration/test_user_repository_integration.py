import pytest
from sqlalchemy import select

from src.infrastructure.persistence.models import Role, User
from src.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository


async def _create_role(repo_session, description: str = "Admin") -> Role:
    role = Role(description=description)
    repo_session.add(role)
    await repo_session.flush()
    await repo_session.commit()
    return role


@pytest.mark.anyio
async def test_create_persists_user_record(repo_session):
    # Arrange
    role = await _create_role(repo_session)
    repository = SqlUserRepository(repo_session)
    # Act
    user = await repository.create(
        name="Bruno",
        email="bruno@fagundes.com",
        password="hashed",
        role_id=role.id,
    )
    await repo_session.commit()
    # Assert
    persisted = await repo_session.scalar(select(User).where(User.id == user.id))
    assert persisted is not None
    assert persisted.email == "bruno@fagundes.com"
    assert persisted.role_id == role.id


@pytest.mark.anyio
async def test_exists_by_email_reflects_database_state(repo_session):
    # Arrange
    role = await _create_role(repo_session, description="Viewer")
    repository = SqlUserRepository(repo_session)
    await repository.create(
        name="Existing",
        email="bruno-exists@fagundes.com",
        password="hashed",
        role_id=role.id,
    )
    await repo_session.commit()
    # Act
    exists = await repository.exists_by_email("bruno-exists@fagundes.com")
    missing = await repository.exists_by_email("bruno-absent@fagundes.com")
    # Assert
    assert exists is True
    assert missing is False


@pytest.mark.anyio
async def test_delete_removes_user_from_database(repo_session):
    # Arrange
    role = await _create_role(repo_session, description="Cleaner")
    repository = SqlUserRepository(repo_session)
    user = await repository.create(
        name="ToDelete",
        email="delete@example.com",
        password="hashed",
        role_id=role.id,
    )
    await repo_session.commit()
    # Act
    await repository.delete(user)
    await repo_session.commit()
    # Assert
    remaining = await repo_session.scalar(select(User).where(User.id == user.id))
    assert remaining is None
