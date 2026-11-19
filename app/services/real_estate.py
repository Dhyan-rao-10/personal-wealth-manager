from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.real_estate import Property


def holdings(db: Session, user_id: int) -> list[tuple[str, object]]:
    """Each property as (name, current value), used by the dashboard and CSV export."""
    properties = db.scalars(select(Property).where(Property.user_id == user_id))
    return [(item.name, item.current_value) for item in properties]
