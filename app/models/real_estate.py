from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.money import ExactDecimal, gain_loss


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(20))
    location: Mapped[str] = mapped_column(String(200))
    purchase_date: Mapped[date] = mapped_column(Date)
    purchase_price: Mapped[Decimal] = mapped_column(ExactDecimal)
    current_value: Mapped[Decimal] = mapped_column(ExactDecimal)

    @property
    def gain_loss(self) -> Decimal:
        return gain_loss(self.current_value, self.purchase_price)[0]

    @property
    def gain_loss_percent(self) -> Decimal:
        return gain_loss(self.current_value, self.purchase_price)[1]
