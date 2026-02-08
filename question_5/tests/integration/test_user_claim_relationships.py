import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from src.infrastructure.persistence.models import Claim, Role, User, UserClaim


@pytest.mark.anyio
async def test_user_claim_unique_constraint_enforced(repo_session):
    # Arrange
    user = User(name="Unique", email="unique@example.com", password="hashed", role_id=0)
    role = Role(description="Admin")
    claim = Claim(description="user:create")
    repo_session.add(role)
    await repo_session.flush()
    user.role_id = role.id
    repo_session.add_all([user, claim])
    await repo_session.flush()
    repo_session.add(UserClaim(user_id=user.id, claim_id=claim.id))
    await repo_session.flush()
    # Act / Assert
    repo_session.add(UserClaim(user_id=user.id, claim_id=claim.id))
    with pytest.raises(IntegrityError):
        await repo_session.flush()


@pytest.mark.anyio
async def test_user_claim_relationship_lists_claims(repo_session):
    # Arrange
    role = Role(description="Admin")
    claim = Claim(description="user:read")
    user = User(name="Reader", email="reader@example.com", password="hashed", role_id=0)
    repo_session.add(role)
    await repo_session.flush()
    user.role_id = role.id
    repo_session.add_all([user, claim])
    await repo_session.flush()
    repo_session.add(UserClaim(user_id=user.id, claim_id=claim.id))
    await repo_session.commit()
    # Act
    result = await repo_session.execute(
        select(User).options(selectinload(User.claims)).where(User.id == user.id),
    )
    db_user = result.scalar_one()
    # Assert
    assert db_user.claims[0].claim_id == claim.id
