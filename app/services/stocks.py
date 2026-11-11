from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.stock import StockHolding


def holdings(db: Session, user_id: int) -> list[tuple[str, object]]:
    """Each holding as (name, current value), used by the dashboard and CSV export."""
    items = db.scalars(select(StockHolding).where(StockHolding.user_id == user_id))
    return [(f"{item.symbol} ({item.exchange})", item.current_value) for item in items]
