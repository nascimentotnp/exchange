from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.entities.entity import CurrencyConversionTransaction


class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_transactions(self, user_id: int, page: int = 1, page_size: int = 10):
        try:
            offset = (page - 1) * page_size

            stmt = (
                select(CurrencyConversionTransaction)
                .filter(CurrencyConversionTransaction.user_id == user_id)
                .order_by(CurrencyConversionTransaction.timestamp.desc())
                .offset(offset)
                .limit(page_size)
            )
            result = await self.db.execute(stmt)
            transactions = result.scalars().all()

            count_stmt = select(func.count()).filter(CurrencyConversionTransaction.user_id == user_id)
            total_result = await self.db.execute(count_stmt)
            total = total_result.scalar_one()

            return transactions, total
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

