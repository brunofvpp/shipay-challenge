from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class UserEntity:
    id: int | None
    name: str
    email: str
    password: str
    role_id: int
    created_at: date
    updated_at: date | None
