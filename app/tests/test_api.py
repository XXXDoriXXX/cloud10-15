from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_root_endpoint(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_user_flow(async_client):

    with patch("app.services.user_service.UserService.create_user", new_callable=AsyncMock) as mock_create:
        mock_create.return_value.email = "test@example.com"
        mock_create.return_value.id = 1

        pass
