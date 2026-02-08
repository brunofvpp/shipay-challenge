from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .claim import Claim
    from .user import User


class UserClaim(SQLModel, table=True):
    __tablename__ = "user_claims"
    __table_args__ = (UniqueConstraint("user_id", "claim_id", name="user_claims_un"),)

    user_id: int = Field(foreign_key="users.id", primary_key=True)
    claim_id: int = Field(foreign_key="claims.id", primary_key=True)

    user: Optional["User"] = Relationship(back_populates="claims")
    claim: Optional["Claim"] = Relationship(back_populates="user_claims")
