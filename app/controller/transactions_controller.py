from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from domain.repository.transaction_repository import TransactionRepository
from entities.entity import User
from gateways.database.connector import get_db
from schemas.currency_conversion_response_schema import CurrencyConversionResponse
from utils.auth_deps import get_current_user
from utils.config.log import current_user_id, current_username

transaction_router = APIRouter(prefix="/transaction", tags=["transaction"])


@transaction_router.get("/{user_id}", response_model=List[CurrencyConversionResponse])
async def get_transactions(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot get transactions of other users"
        )

    current_user_id.set(str(current_user.id))
    current_username.set(current_user.username)

    repo = TransactionRepository(db)

    transactions = await repo.get_user_transactions(user_id)

    return [
        {
            "transaction_id": t.transaction_id,
            "user_id": t.user_id,
            "from_currency": t.from_currency,
            "amount_from": t.amount_from,
            "to_currency": t.to_currency,
            "amount_to": t.amount_to,
            "exchange_rate": t.exchange_rate,
            "timestamp": t.timestamp.isoformat()
        }
        for t in transactions
    ]