from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.domain.repository.transaction_repository import TransactionRepository
from app.entities.entity import User
from app.gateways.database.connector import get_db
from app.schemas.currency_conversion_response_schema import CurrencyConversionResponse
from app.schemas.pagination_schema import PaginatedResponse
from app.utils.auth_deps import get_current_user
from app.utils.config.log import current_user_id, current_username

transaction_router = APIRouter(prefix="/transaction", tags=["transaction"])


@transaction_router.get("/{user_id}", response_model=PaginatedResponse[CurrencyConversionResponse])
async def get_transactions(
        user_id: int,
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é permitido acessar transações de outros usuários"
        )

    current_user_id.set(str(current_user.id))
    current_username.set(current_user.username)

    repo = TransactionRepository(db)
    transactions, total = await repo.get_user_transactions(user_id, page, page_size)

    items = [
        CurrencyConversionResponse(
            transaction_id=t.transaction_id,
            user_id=t.user_id,
            from_currency=t.from_currency,
            amount_from=t.amount_from,
            to_currency=t.to_currency,
            amount_to=t.amount_to,
            exchange_rate=t.exchange_rate,
            timestamp=t.timestamp
        )
        for t in transactions
    ]

    return PaginatedResponse[CurrencyConversionResponse](
        page=page,
        page_size=page_size,
        total=total,
        items=items
    )
