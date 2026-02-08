from datetime import date

import pytest

from src.infrastructure.persistence.models import User
from src.infrastructure.persistence.repositories.sql_user_repository import SqlUserRepository


class FakeAsyncSession:
    def __init__(self, scalar_result=None):
        self.scalar_result = scalar_result
        self.last_query = None
        self.added = []
        self.flush_called = False
        self.deleted = []
        self.refreshed = []
        self.transaction_active = False
        self.committed = False
        self.rolled_back = False

    async def scalar(self, query):
        self.last_query = query
        return self.scalar_result

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flush_called = True
        self.transaction_active = True

    async def delete(self, obj):
        self.deleted.append(obj)
        self.transaction_active = True

    async def refresh(self, obj):
        self.refreshed.append(obj)

    def in_transaction(self):
        return self.transaction_active

    async def commit(self):
        self.committed = True
        self.transaction_active = False

    async def rollback(self):
        self.rolled_back = True
        self.transaction_active = False


@pytest.mark.anyio
async def test_exists_by_email_returns_true_when_match_exists():
    # Arrange
    session = FakeAsyncSession(scalar_result=True)
    repo = SqlUserRepository(session)
    # Act
    result = await repo.exists_by_email("test@fagundes.com")
    # Assert
    assert result is True
    assert "WHERE users.email = :" in str(session.last_query)


@pytest.mark.anyio
async def test_exists_by_email_returns_false_when_no_match_exists():
    # Arrange
    session = FakeAsyncSession(scalar_result=False)
    repo = SqlUserRepository(session)
    # Act
    result = await repo.exists_by_email("missing@fagundes.com")
    # Assert
    assert result is False


@pytest.mark.anyio
async def test_create_persists_user_inside_transaction(monkeypatch):
    fake_today = date(2026, 2, 6)

    class StubDate:
        @staticmethod
        def today():
            return fake_today

    monkeypatch.setattr("src.infrastructure.persistence.repositories.sql_user_repository.date", StubDate)
    # Arrange
    session = FakeAsyncSession()
    repo = SqlUserRepository(session)
    # Act
    user = await repo.create(
        name="Bruno",
        email="bruno@fagundes.com",
        password="hashed",
        role_id=1,
    )
    # Assert
    assert isinstance(user, User)
    assert user.email == "bruno@fagundes.com"
    assert user.created_at == fake_today
    assert user.updated_at is None
    assert session.added[0] is user
    assert session.flush_called is True
