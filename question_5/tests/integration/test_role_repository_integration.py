import pytest

from src.infrastructure.persistence.models import Role
from src.infrastructure.persistence.repositories.sql_role_repository import SqlRoleRepository


@pytest.mark.anyio
async def test_get_by_id_returns_persisted_role(repo_session):
    # Arrange
    role = Role(description="Admin")
    repo_session.add(role)
    await repo_session.flush()
    await repo_session.commit()
    repository = SqlRoleRepository(repo_session)
    # Act
    result = await repository.get_by_id(role.id)
    # Assert
    assert result is not None
    assert result.id == role.id
    assert result.description == "Admin"
