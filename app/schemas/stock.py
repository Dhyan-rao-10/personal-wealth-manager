from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.money import PositiveAmount


class StockIn(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)
    company: str = Field(min_length=1, max_length=100)
    exchange: Literal["NSE", "BSE"]
    quantity: int = Field(gt=0, le=1_000_000_000)
    average_buy_price: PositiveAmount

    @field_validator("symbol")
    @classmethod
    def uppercase_symbol(cls, value: str) -> str:
        return value.strip().upper()


class StockPriceIn(BaseModel):
    current_price: PositiveAmount


class StockOut(StockIn):
    id: int
    current_price: Decimal | None
    current_value: Decimal
    gain_loss: Decimal
    gain_loss_percent: Decimal

    model_config = {"from_attributes": True}
