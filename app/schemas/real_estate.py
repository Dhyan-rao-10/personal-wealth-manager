from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.money import Amount, PositiveAmount


class PropertyIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: Literal["residential", "commercial", "land"]
    location: str = Field(min_length=1, max_length=200)
    purchase_date: date
    purchase_price: PositiveAmount
    current_value: Amount


class PropertyOut(PropertyIn):
    id: int
    gain_loss: Decimal
    gain_loss_percent: Decimal

    model_config = {"from_attributes": True}
