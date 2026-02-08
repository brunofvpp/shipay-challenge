import pytest

from src.infrastructure.persistence.models import Role
from src.infrastructure.persistence.repositories.sql_role_repository import SqlRoleRepository


class FakeAsyncSession:
    def __init__(self, result):
        self.result = result
        self.received_query = None

    async def scalar(self, query):
        self.received_query = query
        return self.result


@pytest.mark.anyio
async def test_get_by_id_returns_role_when_record_exists():
    # Arrange
    fake_session = FakeAsyncSession(Role(id=1, description="Admin"))
    repo = SqlRoleRepository(fake_session)
    # Act
    role = await repo.get_by_id(1)
    # Assert
    assert role is not None
    assert role.description == "Admin"
    assert "WHERE roles.id = :" in str(fake_session.received_query)
