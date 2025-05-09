import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock
from datetime import datetime

from app.main import app
from app.gateways.database.connector import get_db
from app.utils.auth_deps import get_current_user
from app.entities.entity import User


@pytest.fixture()
def mock_db_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture()
def test_user():
    return User(id=1, username="testuser", is_active=True, created_at=datetime.now())


@pytest.fixture(autouse=True)
def override_dependencies(mock_db_session, test_user):
    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_current_user] = lambda: test_user
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
