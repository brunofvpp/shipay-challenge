import pytest

from src.infrastructure.persistence.unit_of_work.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork


class FakeAsyncSession:
    def __init__(self, *, transaction_active: bool) -> None:
        self.transaction_active = transaction_active
        self.commits = 0
        self.rollbacks = 0

    def in_transaction(self) -> bool:
        return self.transaction_active

    async def commit(self) -> None:
        self.commits += 1
        self.transaction_active = False

    async def rollback(self) -> None:
        self.rollbacks += 1
        self.transaction_active = False


@pytest.mark.anyio
async def test_transaction_commits_when_scope_succeeds_and_transaction_is_active():
    # Arrange
    session = FakeAsyncSession(transaction_active=True)
    uow = SqlAlchemyUnitOfWork(session)

    # Act
    async with uow.transaction():
        pass

    # Assert
    assert session.commits == 1
    assert session.rollbacks == 0


@pytest.mark.anyio
async def test_transaction_does_not_commit_when_no_transaction_is_active():
    # Arrange
    session = FakeAsyncSession(transaction_active=False)
    uow = SqlAlchemyUnitOfWork(session)

    # Act
    async with uow.transaction():
        pass

    # Assert
    assert session.commits == 0
    assert session.rollbacks == 0


@pytest.mark.anyio
async def test_transaction_rolls_back_and_reraises_when_scope_fails_and_transaction_is_active():
    # Arrange
    session = FakeAsyncSession(transaction_active=True)
    uow = SqlAlchemyUnitOfWork(session)

    # Act
    with pytest.raises(RuntimeError, match="boom"):
        async with uow.transaction():
            raise RuntimeError("boom")

    # Assert
    assert session.commits == 0
    assert session.rollbacks == 1


@pytest.mark.anyio
async def test_transaction_reraises_without_rollback_when_no_transaction_is_active():
    # Arrange
    session = FakeAsyncSession(transaction_active=False)
    uow = SqlAlchemyUnitOfWork(session)

    # Act
    with pytest.raises(RuntimeError, match="boom"):
        async with uow.transaction():
            raise RuntimeError("boom")

    # Assert
    assert session.commits == 0
    assert session.rollbacks == 0
