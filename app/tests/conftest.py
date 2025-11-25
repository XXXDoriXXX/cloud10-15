import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.main import app

settings.DATABASE_URL = "sqlite+aiosqlite:///:memory:"
settings.ENVIRONMENT = "test"


@pytest.fixture(scope="session")
def event_loop():

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def async_client():

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
