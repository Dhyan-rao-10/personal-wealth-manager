from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.money import PositiveAmount


class GoldIn(BaseModel):
    description: str = Field(min_length=1, max_length=100)
    form: Literal["coin", "bar", "jewellery", "digital"]
    weight_grams: Decimal = Field(gt=0, max_digits=10, decimal_places=3)
    purity: Literal["24K", "22K", "18K"]
    purchase_date: date
    purchase_price: PositiveAmount


class GoldOut(GoldIn):
    id: int
    current_value: Decimal


class GoldPriceIn(BaseModel):
    price_per_gram: PositiveAmount


class GoldPriceOut(BaseModel):
    price_per_gram: Decimal | None
