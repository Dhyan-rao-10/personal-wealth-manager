from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.money import Amount, PositiveAmount


class CashAccountIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: Literal["cash", "bank", "wallet"]
    opening_balance: Amount


class CashAccountOut(CashAccountIn):
    id: int
    balance: Decimal

    model_config = {"from_attributes": True}


class TransactionIn(BaseModel):
    type: Literal["deposit", "withdrawal"]
    amount: PositiveAmount
    note: str = Field(default="", max_length=200)


class TransactionOut(TransactionIn):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
