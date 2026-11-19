from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_owned
from app.models.real_estate import Property
from app.models.user import User
from app.schemas.real_estate import PropertyIn, PropertyOut

router = APIRouter(prefix="/api/real-estate", tags=["real estate"])


@router.get("", response_model=list[PropertyOut])
def list_properties(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Property).where(Property.user_id == user.id)).all()


@router.post("", response_model=PropertyOut, status_code=status.HTTP_201_CREATED)
def add_property(
    data: PropertyIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    item = Property(user_id=user.id, **data.model_dump())
    db.add(item)
    db.commit()
    return item


@router.put("/{item_id}", response_model=PropertyOut)
def edit_property(
    item_id: int,
    data: PropertyIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = get_owned(db, Property, item_id, user)
    for field, value in data.model_dump().items():
        setattr(item, field, value)
    db.commit()
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    db.delete(get_owned(db, Property, item_id, user))
    db.commit()
