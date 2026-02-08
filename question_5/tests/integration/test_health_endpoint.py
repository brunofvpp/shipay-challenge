import pytest


@pytest.mark.anyio
async def test_health_endpoint_returns_ok_status_payload(api_client):
    # Arrange
    # Act
    async with api_client() as client:
        response = await client.get("/v1/health")
    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
