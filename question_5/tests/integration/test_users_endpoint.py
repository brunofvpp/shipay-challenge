from datetime import date

import pytest

from src.application.exceptions import EmailAlreadyExistsError, RoleNotFoundError
from src.application.schemas import UserCreateInput, UserOutput
from src.presentation import deps


class FakeUserService:
    def __init__(self, *, result: UserOutput | None = None, error: Exception | None = None):
        self.result = result
        self.error = error
        self.calls: list[UserCreateInput] = []

    async def create_user(self, payload: UserCreateInput) -> UserOutput:
        self.calls.append(payload)
        if self.error:
            raise self.error
        assert self.result is not None
        return self.result


@pytest.mark.anyio
async def test_create_user_returns_201_with_service_result(api_client):
    # Arrange
    user_output = UserOutput(
        id=1,
        name="Bruno",
        email="bruno@fagundes.com",
        role_id=1,
        created_at=date(2026, 2, 6),
        updated_at=None,
    )
    fake_service = FakeUserService(result=user_output)

    # Act
    async def _override():
        return fake_service

    async with api_client({deps.get_user_service: _override}) as client:
        response = await client.post(
            "/v1/users",
            json={"name": "Bruno", "email": "bruno@fagundes.com", "role_id": 1, "password": "Senha123!"},
        )

    # Assert
    assert response.status_code == 201
    assert response.json() == user_output.model_dump(mode="json")
    assert fake_service.calls[0].email == "bruno@fagundes.com"


@pytest.mark.anyio
async def test_create_user_returns_409_when_service_detects_conflict(api_client):
    # Arrange
    fake_service = FakeUserService(error=EmailAlreadyExistsError("bruno-exists@fagundes.com"))

    # Act
    async def _override():
        return fake_service

    async with api_client({deps.get_user_service: _override}) as client:
        response = await client.post(
            "/v1/users",
            json={"name": "Bruno", "email": "bruno-exists@fagundes.com", "role_id": 1, "password": "Senha123!"},
        )

    # Assert
    assert response.status_code == 409
    payload = response.json()
    assert payload["type"] == "email-already-exists"
    assert "bruno-exists@fagundes.com" in payload["detail"]


@pytest.mark.anyio
async def test_create_user_returns_500_on_unhandled_service_error(api_client):
    # Arrange
    fake_service = FakeUserService(error=RuntimeError("boom"))

    # Act
    async def _override():
        return fake_service

    async with api_client({deps.get_user_service: _override}) as client:
        response = await client.post(
            "/v1/users",
            json={"name": "Bruno", "email": "error@fagundes.com", "role_id": 1, "password": "Senha123!"},
        )

    # Assert
    assert response.status_code == 500
    payload = response.json()
    assert payload["type"] == "internal-server-error"
    assert payload["title"] == "Internal server error"


@pytest.mark.anyio
async def test_create_user_returns_404_when_role_missing(api_client):
    # Arrange
    fake_service = FakeUserService(error=RoleNotFoundError(99))

    # Act
    async def _override():
        return fake_service

    async with api_client({deps.get_user_service: _override}) as client:
        response = await client.post(
            "/v1/users",
            json={"name": "Bruno", "email": "norole@fagundes.com", "role_id": 99, "password": "Senha123!"},
        )

    # Assert
    assert response.status_code == 404
    body = response.json()
    assert body["type"] == "role-not-found"
    assert "99" in body["detail"]


@pytest.mark.anyio
async def test_create_user_returns_422_for_invalid_payload(api_client):
    # Arrange
    fake_service = FakeUserService()

    # Act
    async def _override():
        return fake_service

    async with api_client({deps.get_user_service: _override}) as client:
        response = await client.post(
            "/v1/users",
            json={"name": "", "email": "not-email", "role_id": 0, "password": "short"},
        )

    # Assert
    assert response.status_code == 422
