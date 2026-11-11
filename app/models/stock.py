from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.money import ExactDecimal, gain_loss, round_money


class StockHolding(Base):
    __tablename__ = "stock_holdings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    symbol: Mapped[str] = mapped_column(String(20))
    company: Mapped[str] = mapped_column(String(100))
    exchange: Mapped[str] = mapped_column(String(3))
    quantity: Mapped[int] = mapped_column(Integer)
    average_buy_price: Mapped[Decimal] = mapped_column(ExactDecimal)
    current_price: Mapped[Decimal | None] = mapped_column(ExactDecimal, default=None)

    @property
    def current_value(self) -> Decimal:
        """quantity x price. Uses the buy price until a current price is set."""
        price = self.average_buy_price if self.current_price is None else self.current_price
        return round_money(self.quantity * price)

    @property
    def gain_loss(self) -> Decimal:
        return gain_loss(self.current_value, self.quantity * self.average_buy_price)[0]

    @property
    def gain_loss_percent(self) -> Decimal:
        return gain_loss(self.current_value, self.quantity * self.average_buy_price)[1]
