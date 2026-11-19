from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.money import ExactDecimal


class GoldHolding(Base):
    __tablename__ = "gold_holdings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    description: Mapped[str] = mapped_column(String(100))
    form: Mapped[str] = mapped_column(String(20))
    weight_grams: Mapped[Decimal] = mapped_column(ExactDecimal)
    purity: Mapped[str] = mapped_column(String(3))
    purchase_date: Mapped[date] = mapped_column(Date)
    purchase_price: Mapped[Decimal] = mapped_column(ExactDecimal)


class GoldPrice(Base):
    """The price per gram of 24K gold that this user last entered."""

    __tablename__ = "gold_prices"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    price_per_gram: Mapped[Decimal] = mapped_column(ExactDecimal)
