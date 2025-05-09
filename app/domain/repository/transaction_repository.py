from sqlalchemy import Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from entities.entity import CurrencyConversionTransaction
from typing import List, Any, Sequence


class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_transactions(self, user_id: int):
        try:
            result = await self.db.execute(
                select(CurrencyConversionTransaction)
                .filter(CurrencyConversionTransaction.user_id == user_id)
                .order_by(CurrencyConversionTransaction.timestamp.desc())
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
