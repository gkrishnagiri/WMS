from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.core.config import Settings


class _UnavailableDatabase:
    git_commit = "test-commit"

    def check_connection(self) -> bool:
        return False


class _UnavailableRedis:
    async def ping(self) -> bool:
        return False


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    # Endpoint tests do not require external services. Their unavailable
    # dependency doubles make the 503 health path deterministic; running the
    # real service checks is an integration concern for a live environment.
    app.state.settings = Settings()
    app.state.database = _UnavailableDatabase()
    app.state.redis = _UnavailableRedis()
    app.state.build_timestamp = "test-build"
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as test_client:
        yield test_client
