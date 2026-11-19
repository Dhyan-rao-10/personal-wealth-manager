from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.gold import GoldHolding, GoldPrice
from app.money import round_money
from app.schemas.gold import GoldIn, GoldOut


def current_price(db: Session, user_id: int) -> Decimal | None:
    price = db.get(GoldPrice, user_id)
    return price.price_per_gram if price else None


def set_price(db: Session, user_id: int, price_per_gram: Decimal) -> None:
    price = db.get(GoldPrice, user_id)
    if price:
        price.price_per_gram = price_per_gram
    else:
        db.add(GoldPrice(user_id=user_id, price_per_gram=price_per_gram))
    db.commit()


def value_of(holding: GoldHolding, price_per_gram: Decimal | None) -> Decimal:
    """weight x (purity / 24) x price. Uses the purchase price until a gold price is set."""
    if price_per_gram is None:
        return holding.purchase_price
    karat = int(holding.purity.removesuffix("K"))
    return round_money(holding.weight_grams * karat * price_per_gram / 24)


def to_response(holding: GoldHolding, price_per_gram: Decimal | None) -> GoldOut:
    fields = {name: getattr(holding, name) for name in GoldIn.model_fields}
    return GoldOut(**fields, id=holding.id, current_value=value_of(holding, price_per_gram))


def holdings(db: Session, user_id: int) -> list[tuple[str, Decimal]]:
    """Each holding as (name, current value), used by the dashboard and CSV export."""
    price = current_price(db, user_id)
    items = db.scalars(select(GoldHolding).where(GoldHolding.user_id == user_id))
    return [(item.description, value_of(item, price)) for item in items]
