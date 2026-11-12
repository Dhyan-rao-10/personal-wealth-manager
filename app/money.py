"""Exact decimal handling for money. Floats are never used for amounts."""
from decimal import ROUND_HALF_UP, Decimal
from typing import Annotated

from pydantic import AfterValidator, Field
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

TWO_PLACES = Decimal("0.01")


class ExactDecimal(TypeDecorator):
    """Stores a Decimal as text, because SQLite would otherwise turn it into a float."""

    impl = String(40)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return None if value is None else str(value)

    def process_result_value(self, value, dialect):
        return None if value is None else Decimal(value)


def round_money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


# Request field types: at most 2 decimal places, no negatives, always saved as 0.00.
Amount = Annotated[
    Decimal, Field(ge=0, max_digits=15, decimal_places=2), AfterValidator(round_money)
]
PositiveAmount = Annotated[
    Decimal, Field(gt=0, max_digits=15, decimal_places=2), AfterValidator(round_money)
]


def gain_loss(current: Decimal, cost: Decimal) -> tuple[Decimal, Decimal]:
    """Returns the gain (or loss, if negative) in rupees and as a percentage of cost."""
    gain = round_money(current - cost)
    percent = round_money(gain / cost * 100) if cost else Decimal("0.00")
    return gain, percent
