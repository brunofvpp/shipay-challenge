import pytest
from sqlalchemy import select

from src.infrastructure.persistence.models import Role, User


@pytest.mark.anyio
async def test_create_user_e2e_persists_user_and_returns_201(e2e_client):
    # Arrange
    client, session = e2e_client
    role = Role(description="admin")
    session.add(role)
    await session.flush()
    await session.commit()
    # Act
    response = await client.post(
        "/v1/users",
        json={
            "name": "Bruno",
            "email": "bruno@fagundes.com",
            "role_id": role.id,
            "password": "Senha123!",
        },
    )
    # Assert
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "bruno@fagundes.com"
    assert body["role_id"] == role.id
    persisted = await session.scalar(select(User).where(User.email == "bruno@fagundes.com"))
    assert persisted is not None
    assert persisted.password != "Senha123!"


@pytest.mark.anyio
async def test_create_user_e2e_returns_409_when_email_already_exists(e2e_client):
    # Arrange
    client, session = e2e_client
    role = Role(description="admin")
    session.add(role)
    await session.flush()
    await session.commit()
    payload = {
        "name": "Bruno",
        "email": "bruno-dup@fagundes.com",
        "role_id": role.id,
        "password": "Senha123!",
    }
    # Act
    first_response = await client.post("/v1/users", json=payload)
    second_response = await client.post("/v1/users", json=payload)
    # Assert
    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["type"] == "email-already-exists"


@pytest.mark.anyio
async def test_create_user_e2e_returns_404_when_role_does_not_exist(e2e_client):
    # Arrange
    client, _ = e2e_client
    # Act
    response = await client.post(
        "/v1/users",
        json={
            "name": "Bruno",
            "email": "norole@fagundes.com",
            "role_id": 999,
            "password": "Senha123!",
        },
    )
    # Assert
    assert response.status_code == 404
    assert response.json()["type"] == "role-not-found"
