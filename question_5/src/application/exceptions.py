from dataclasses import dataclass, field
from typing import Any, Mapping


class ServiceError(RuntimeError):
    """Base class for service layer errors."""


@dataclass(slots=True)
class RFC7807Exception(ServiceError):
    status_code: int
    title: str
    detail: str
    kind: str = "generic"
    extra: Mapping[str, Any] | None = field(default=None)

    def to_dict(self, *, instance: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "type": self.kind,
            "title": self.title,
            "status": self.status_code,
            "detail": self.detail,
        }
        if instance:
            payload["instance"] = instance
        if self.extra:
            payload.update(self.extra)
        return payload


class InternalServerError(RFC7807Exception):
    def __init__(self, detail: str = "Unexpected server error.") -> None:
        super().__init__(
            status_code=500,
            title="Internal server error",
            detail=detail,
            kind="internal-server-error",
        )


class NotFoundError(RFC7807Exception):
    def __init__(self, detail: str, *, kind: str = "not-found", extra: Mapping[str, Any] | None = None) -> None:
        super().__init__(status_code=404, title="Resource not found", detail=detail, kind=kind, extra=extra)


class ConflictError(RFC7807Exception):
    def __init__(self, detail: str, *, kind: str = "conflict", extra: Mapping[str, Any] | None = None) -> None:
        super().__init__(status_code=409, title="Resource conflict", detail=detail, kind=kind, extra=extra)


class RoleNotFoundError(NotFoundError):
    def __init__(self, role_id: Any) -> None:
        super().__init__(
            detail=f"Role with id '{role_id}' was not found",
            kind="role-not-found",
            extra={"role_id": role_id},
        )


class EmailAlreadyExistsError(ConflictError):
    def __init__(self, email: str) -> None:
        super().__init__(
            detail=f"Email '{email}' is already registered",
            kind="email-already-exists",
            extra={"email": email},
        )
