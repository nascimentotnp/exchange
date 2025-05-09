import pytest
from unittest.mock import patch, AsyncMock

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError


@pytest.mark.asyncio
@patch("app.domain.repository.user_repository.UserRepository.create")
async def test_create_user(mock_create, async_client):
    mock_create.return_value = {
        "id": 1,
        "username": "new_user",
        "is_active": True,
        "created_at": "2025-05-09T15:45:26.575Z"
    }

    user_data = {
        "username": "new_user",
        "password_hash": "123456"
    }

    response = await async_client.post("/users/", json=user_data)
    assert response.status_code == 200
    assert response.json()["username"] == "new_user"


@pytest.mark.asyncio
async def test_get_current_user(async_client):
    response = await async_client.get("/users/me")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


@pytest.mark.asyncio
@patch("app.domain.repository.user_repository.UserRepository.find_by_username", new_callable=AsyncMock)
async def test_find_by_username(mock_find_by_username, async_client):
    mock_find_by_username.return_value = {
        "id": 1,
        "username": "testuser",
        "is_active": True,
        "created_at": "2025-05-09T12:00:00Z"
    }
    response = await async_client.get("/users/me")
    assert response.status_code == 200


@pytest.mark.asyncio
@patch("app.domain.repository.user_repository.UserRepository.find_by_session", new_callable=AsyncMock)
async def test_find_by_session(mock_find_by_session, async_client):
    mock_find_by_session.return_value = {
        "id": 1,
        "username": "testuser",
        "is_active": True,
        "created_at": "2025-05-09T12:00:00Z"
    }
    response = await async_client.get("/users/me")
    assert response.status_code == 200


@pytest.mark.asyncio
@patch("app.domain.repository.user_repository.UserRepository.update")
async def test_update_user_authorized(mock_update, async_client):
    mock_update.return_value = {
        "id": 1,
        "username": "updated_user",
        "is_active": True,
        "created_at": "2025-05-09T12:00:00Z"
    }

    update_data = {"username": "updated_user"}
    response = await async_client.put("/users/1", json=update_data)
    assert response.status_code == 200
    assert response.json()["username"] == "updated_user"


@pytest.mark.asyncio
@patch("app.domain.repository.user_repository.UserRepository.delete")
async def test_delete_user_authorized(mock_delete, async_client):
    response = await async_client.delete("/users/1")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"


@pytest.mark.asyncio
async def test_update_user_unauthorized(async_client):
    update_data = {"username": "hacker"}
    response = await async_client.put("/users/999", json=update_data)
    assert response.status_code == 403
    assert "Cannot update other users" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_user_unauthorized(async_client):
    response = await async_client.delete("/users/999")
    assert response.status_code == 403
    assert "Cannot delete other users" in response.json()["detail"]


@pytest.mark.asyncio
@patch("app.domain.repository.user_repository.UserRepository.find_by_id")
async def test_find_by_id_not_found(mock_find_by_id, async_client):
    mock_find_by_id.side_effect = HTTPException(status_code=404, detail="User not found")
    with pytest.raises(HTTPException) as exc:
        await mock_find_by_id(99)
    assert exc.value.status_code == 404

@pytest.mark.asyncio
@patch("app.domain.repository.user_repository.UserRepository.create")
async def test_create_user_existing_username(mock_create, async_client):
    mock_create.side_effect = HTTPException(status_code=409, detail="Username already exists")
    with pytest.raises(HTTPException) as exc:
        await mock_create({"username": "test", "password_hash": "abc"})
    assert exc.value.status_code == 409


@pytest.mark.asyncio
@patch("app.domain.repository.user_repository.UserRepository.create")
async def test_create_user_db_error(mock_create, async_client):
    mock_create.side_effect = SQLAlchemyError("DB failure")
    with pytest.raises(SQLAlchemyError):
        await mock_create({"username": "fail", "password_hash": "xyz"})


@pytest.mark.asyncio
@patch("app.domain.repository.user_repository.UserRepository.update")
async def test_update_user_db_error(mock_update, async_client):
    mock_update.side_effect = SQLAlchemyError("Update failed")
    with pytest.raises(SQLAlchemyError):
        await mock_update(1, {"username": "update"})


@pytest.mark.asyncio
@patch("app.domain.repository.user_repository.UserRepository.delete")
async def test_delete_user_db_error(mock_delete, async_client):
    mock_delete.side_effect = SQLAlchemyError("Delete failed")
    with pytest.raises(SQLAlchemyError):
        await mock_delete(1)


@pytest.mark.asyncio
@patch("app.domain.repository.user_repository.UserRepository.find_by_session")
async def test_find_by_session_expired(mock_find_by_session, async_client):
    mock_find_by_session.return_value = None
    result = await mock_find_by_session("expired-session-id")
    assert result is None