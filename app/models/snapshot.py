from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.money import ExactDecimal


class NetWorthSnapshot(Base):
    """A user's net worth on one date. There is at most one per user per day."""

    __tablename__ = "net_worth_snapshots"
    __table_args__ = (UniqueConstraint("user_id", "date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date: Mapped[date] = mapped_column(Date)
    net_worth: Mapped[Decimal] = mapped_column(ExactDecimal)
