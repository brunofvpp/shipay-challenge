from dataclasses import dataclass


@dataclass(slots=True)
class RoleEntity:
    id: int
    description: str
