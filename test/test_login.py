from unittest.mock import patch, AsyncMock

import pytest
from fastapi import HTTPException

from app.utils.password import hash_password


@pytest.mark.asyncio
@patch("app.domain.service.auth_service.AuthService.login")
async def test_login_success(mock_login, async_client):
    mock_login.return_value = {
        "user": type("User", (), {"id": 1, "username": "admin"})()
    }

    response = await async_client.post("/auth/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    assert response.json()["username"] == "admin"


@pytest.mark.asyncio
@patch("app.domain.service.auth_service.AuthService.login")
async def test_login_failure(mock_login, async_client):
    from fastapi import HTTPException
    mock_login.side_effect = HTTPException(status_code=401, detail="Invalid credentials")

    response = await async_client.post("/auth/login", json={"username": "wrong", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
@patch("app.domain.service.auth_service.UserRepository")
async def test_login_invalid_user(mock_repo, async_client):
    instance = mock_repo.return_value
    instance.find_by_username = AsyncMock(side_effect=HTTPException(status_code=401, detail="User not found"))

    response = await async_client.post("/auth/login", json={"username": "fake", "password": "fake"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_without_session(async_client):
    response = await async_client.post("/auth/logout")
    assert response.status_code == 401


@patch("app.domain.service.auth_service.UserRepository")
async def test_login_invalid_password(mock_repo, async_client):
    user = type("User", (), {"id": 1, "username": "admin", "password_hash": "hashed"})()
    instance = mock_repo.return_value
    instance.find_by_username = AsyncMock(return_value=user)

    with patch("app.domain.service.auth_service.pwd_context.verify", return_value=False):
        response = await async_client.post("/auth/login", json={"username": "admin", "password": "wrong"})
        assert response.status_code == 401


def test_hash_password():
    hashed = hash_password("abc123")
    assert hashed.startswith("$2b$")
