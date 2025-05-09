from typing import Union

from pydantic import BaseModel


class ExchangeRateInfo(BaseModel):
    timestamp: int
    rate: float


class ExchangeRateQuery(BaseModel):
    from_currency: str
    to_currency: str
    amount: Union[str, float]


class ExchangeRateResponse(BaseModel):
    success: bool
    query: ExchangeRateQuery
    info: ExchangeRateInfo
    result: float
    date: str
