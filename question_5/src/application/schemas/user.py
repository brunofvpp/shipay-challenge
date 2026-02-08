from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, PositiveInt, field_validator


class UserCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    role_id: PositiveInt
    password: Optional[str] = Field(default=None, min_length=8, max_length=255)

    @field_validator("password")
    @classmethod
    def _validate_password(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not value.strip():
            raise ValueError("password cannot be blank")
        return value


class UserOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: PositiveInt
    name: str
    email: EmailStr
    role_id: PositiveInt
    created_at: date
    updated_at: Optional[date]
