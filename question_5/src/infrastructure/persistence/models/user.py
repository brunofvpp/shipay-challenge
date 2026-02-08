from datetime import date
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .role import Role
    from .user_claim import UserClaim


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=255)
    role_id: int = Field(foreign_key="roles.id")
    created_at: date = Field(default_factory=date.today)
    updated_at: Optional[date] = Field(default=None)

    role: Optional["Role"] = Relationship(back_populates="users")
    claims: List["UserClaim"] = Relationship(back_populates="user")
