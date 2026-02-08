import pytest

from src.infrastructure.persistence.repositories.base import BaseRepository


class FakeAsyncSession:
    def __init__(self) -> None:
        self.added = []
        self.deleted = []
        self.refreshed = []
        self.flush_calls = 0
        self.commits = 0
        self.rollbacks = 0
        self.transaction_active = False

    def add(self, instance):
        self.added.append(instance)

    async def delete(self, instance):
        self.deleted.append(instance)
        self.transaction_active = True

    async def flush(self):
        self.flush_calls += 1
        self.transaction_active = True

    async def refresh(self, instance):
        self.refreshed.append(instance)

    def in_transaction(self):
        return self.transaction_active

    async def commit(self):
        self.commits += 1
        self.transaction_active = False

    async def rollback(self):
        self.rollbacks += 1
        self.transaction_active = False


class DummyRepository(BaseRepository): ...


@pytest.mark.anyio
async def test_save_adds_instance_and_flushes():
    # Arrange
    session = FakeAsyncSession()
    repo = DummyRepository(session)
    instance = object()
    # Act
    result = await repo.save(instance)
    # Assert
    assert result is instance
    assert session.added == [instance]
    assert session.flush_calls == 1
    assert session.refreshed == []


@pytest.mark.anyio
async def test_save_refreshes_instance_when_requested():
    # Arrange
    session = FakeAsyncSession()
    repo = DummyRepository(session)
    instance = object()
    # Act
    await repo.save(instance, refresh=True)
    # Assert
    assert session.refreshed == [instance]


@pytest.mark.anyio
async def test_delete_removes_instance_and_flushes():
    # Arrange
    session = FakeAsyncSession()
    repo = DummyRepository(session)
    instance = object()
    # Act
    await repo.delete(instance)
    # Assert
    assert session.deleted == [instance]
    assert session.flush_calls == 1
    assert session.transaction_active is True


@pytest.mark.anyio
async def test_commit_executes_only_when_transaction_active():
    # Arrange
    session = FakeAsyncSession()
    repo = DummyRepository(session)
    session.transaction_active = True
    # Act
    await repo.commit()
    # Assert
    assert session.commits == 1
    assert session.transaction_active is False


@pytest.mark.anyio
async def test_commit_skips_when_transaction_inactive():
    # Arrange
    session = FakeAsyncSession()
    repo = DummyRepository(session)
    # Act
    await repo.commit()
    # Assert
    assert session.commits == 0


@pytest.mark.anyio
async def test_rollback_executes_only_when_transaction_active():
    # Arrange
    session = FakeAsyncSession()
    repo = DummyRepository(session)
    session.transaction_active = True
    # Act
    await repo.rollback()
    # Assert
    assert session.rollbacks == 1
    assert session.transaction_active is False


@pytest.mark.anyio
async def test_transaction_commits_on_success():
    # Arrange
    session = FakeAsyncSession()
    repo = DummyRepository(session)
    # Act
    async with repo.transaction():
        session.transaction_active = True
    # Assert
    assert session.commits == 1
    assert session.rollbacks == 0


@pytest.mark.anyio
async def test_transaction_rolls_back_on_exception():
    # Arrange
    session = FakeAsyncSession()
    repo = DummyRepository(session)
    # Act & Assert
    with pytest.raises(RuntimeError):
        async with repo.transaction():
            session.transaction_active = True
            raise RuntimeError("boom")
    assert session.commits == 0
    assert session.rollbacks == 1


@pytest.mark.anyio
async def test_refresh_delegates_to_session_refresh():
    # Arrange
    session = FakeAsyncSession()
    repo = DummyRepository(session)
    instance = object()
    # Act
    await repo.refresh(instance)
    # Assert
    assert session.refreshed == [instance]
