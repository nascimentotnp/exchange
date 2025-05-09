from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class CurrencyConversionResponse(BaseModel):
    transaction_id: str
    user_id: int
    from_currency: str
    amount_from: float
    to_currency: str
    amount_to: float
    exchange_rate: float
    timestamp: datetime

    class Config:
        from_attributes = True
