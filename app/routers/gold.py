from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_owned
from app.models.gold import GoldHolding
from app.models.user import User
from app.schemas.gold import GoldIn, GoldOut, GoldPriceIn, GoldPriceOut
from app.services import gold

router = APIRouter(prefix="/api/gold", tags=["gold"])


@router.get("/price", response_model=GoldPriceOut)
def get_price(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"price_per_gram": gold.current_price(db, user.id)}


@router.put("/price", response_model=GoldPriceOut)
def set_price(
    data: GoldPriceIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    gold.set_price(db, user.id, data.price_per_gram)
    return data


@router.get("", response_model=list[GoldOut])
def list_gold(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    price = gold.current_price(db, user.id)
    items = db.scalars(select(GoldHolding).where(GoldHolding.user_id == user.id))
    return [gold.to_response(item, price) for item in items]


@router.post("", response_model=GoldOut, status_code=status.HTTP_201_CREATED)
def add_gold(data: GoldIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = GoldHolding(user_id=user.id, **data.model_dump())
    db.add(item)
    db.commit()
    return gold.to_response(item, gold.current_price(db, user.id))


@router.put("/{item_id}", response_model=GoldOut)
def edit_gold(
    item_id: int,
    data: GoldIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = get_owned(db, GoldHolding, item_id, user)
    for field, value in data.model_dump().items():
        setattr(item, field, value)
    db.commit()
    return gold.to_response(item, gold.current_price(db, user.id))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gold(
    item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    db.delete(get_owned(db, GoldHolding, item_id, user))
    db.commit()
