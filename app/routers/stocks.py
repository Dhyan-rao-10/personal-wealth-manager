from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_owned
from app.models.stock import StockHolding
from app.models.user import User
from app.schemas.stock import StockIn, StockOut, StockPriceIn

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("", response_model=list[StockOut])
def list_stocks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(StockHolding).where(StockHolding.user_id == user.id)).all()


@router.post("", response_model=StockOut, status_code=status.HTTP_201_CREATED)
def add_stock(data: StockIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = StockHolding(user_id=user.id, **data.model_dump())
    db.add(item)
    db.commit()
    return item


@router.put("/{item_id}", response_model=StockOut)
def edit_stock(
    item_id: int,
    data: StockIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = get_owned(db, StockHolding, item_id, user)
    for field, value in data.model_dump().items():
        setattr(item, field, value)
    db.commit()
    return item


@router.put("/{item_id}/price", response_model=StockOut)
def update_price(
    item_id: int,
    data: StockPriceIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = get_owned(db, StockHolding, item_id, user)
    item.current_price = data.current_price
    db.commit()
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stock(
    item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    db.delete(get_owned(db, StockHolding, item_id, user))
    db.commit()
