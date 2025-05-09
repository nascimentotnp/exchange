from datetime import datetime

import pytest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.domain.repository.transaction_repository import TransactionRepository


@pytest.mark.asyncio
@patch("app.domain.repository.transaction_repository.TransactionRepository.get_user_transactions",
       new_callable=AsyncMock)
async def test_get_transactions(mock_get_tx, async_client):
    mock_get_tx.return_value = (
        [
            type("Tx", (), {
                "transaction_id": "uuid-123",
                "user_id": 1,
                "from_currency": "USD",
                "amount_from": 10.0,
                "to_currency": "BRL",
                "amount_to": 50.0,
                "exchange_rate": 5.0,
                "timestamp": datetime.fromisoformat("2025-05-09T12:00:00Z")
            })()
        ],
        1
    )

    response = await async_client.get("/transaction/1")
    assert response.status_code == 200
    assert isinstance(response.json()["items"], list)


@pytest.mark.asyncio
async def test_get_transactions_unauthorized(async_client):
    response = await async_client.get("/transaction/999")
    assert response.status_code == 403


@patch("app.domain.repository.transaction_repository.AsyncSession.execute")
async def test_get_user_transactions_exception(mock_exec, async_client):
    mock_exec.side_effect = SQLAlchemyError("DB Error")
    repo = TransactionRepository(mock_db_session())
    with pytest.raises(HTTPException):
        await repo.get_user_transactions(user_id=1)


@pytest.mark.asyncio
async def test_get_user_transactions_db_error(mock_db_session):
    mock_db_session.execute.side_effect = SQLAlchemyError("broken")
    repo = TransactionRepository(mock_db_session)
    with pytest.raises(HTTPException) as exc:
        await repo.get_user_transactions(user_id=1)
    assert exc.value.status_code == 500
