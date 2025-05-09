import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.entity import User, CurrencyConversionTransaction
from app.gateways.database.connector import get_db
from app.gateways.external_api.apilayer_gateway import fetch_exchange_rate
from app.schemas.currency_conversion_response_schema import CurrencyConversionResponse
from app.utils.auth_deps import get_current_user
from app.utils.config.log import get_logger

exchange_router = APIRouter(prefix="/exchange", tags=["exchange"])

valid_currencies = ["BRL", "USD", "EUR", "JPY"]
logger = get_logger(__name__)


@exchange_router.get("/convert/{from_currency}/{to_currency}/{amount}", response_model=CurrencyConversionResponse)
async def convert_currency(
        from_currency: str,
        to_currency: str,
        amount: float,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    if from_currency not in valid_currencies or to_currency not in valid_currencies:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid currency. Valid currencies are: {', '.join(valid_currencies)}"
        )
    if amount < 0:
        raise HTTPException(status_code=400, detail="Amount must be non-negative")

    try:
        exchange_data = fetch_exchange_rate(from_currency, to_currency, amount)
        transaction = CurrencyConversionTransaction(
            transaction_id=str(uuid.uuid4()),
            user_id=current_user.id,
            from_currency=from_currency.upper(),
            amount_from=amount,
            to_currency=to_currency.upper(),
            amount_to=exchange_data['result'],
            exchange_rate=exchange_data['rate'],
            timestamp=datetime.now(timezone.utc)
        )
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        exchange = CurrencyConversionResponse(
            transaction_id=transaction.transaction_id,
            user_id=transaction.user_id,
            from_currency=transaction.from_currency,
            amount_from=transaction.amount_from,
            to_currency=transaction.to_currency,
            amount_to=transaction.amount_to,
            exchange_rate=transaction.exchange_rate,
            timestamp=transaction.timestamp.isoformat()
        )
        logger.info(exchange)

        return exchange

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Conversion failed: {str(e)}"
        )
