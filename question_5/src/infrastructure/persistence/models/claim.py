from typing import TYPE_CHECKING, List

from sqlalchemy import text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user_claim import UserClaim


class Claim(SQLModel, table=True):
    __tablename__ = "claims"

    id: int | None = Field(default=None, primary_key=True)
    description: str = Field(min_length=1, max_length=255)
    active: bool = Field(default=True, sa_column_kwargs={"server_default": text("TRUE")})
    user_claims: List["UserClaim"] = Relationship(back_populates="claim")
