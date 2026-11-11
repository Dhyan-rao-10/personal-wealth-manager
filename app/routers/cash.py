from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_owned
from app.models.cash import CashAccount, CashTransaction
from app.models.user import User
from app.schemas.cash import CashAccountIn, CashAccountOut, TransactionIn, TransactionOut
from app.services import cash

router = APIRouter(prefix="/api/cash", tags=["cash"])


@router.get("", response_model=list[CashAccountOut])
def list_accounts(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(CashAccount).where(CashAccount.user_id == user.id)).all()


@router.post("", response_model=CashAccountOut, status_code=status.HTTP_201_CREATED)
def add_account(
    data: CashAccountIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    account = CashAccount(user_id=user.id, balance=data.opening_balance, **data.model_dump())
    db.add(account)
    db.commit()
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    db.delete(get_owned(db, CashAccount, account_id, user))
    db.commit()


@router.get("/{account_id}/transactions", response_model=list[TransactionOut])
def list_transactions(
    account_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    get_owned(db, CashAccount, account_id, user)
    newest_first = (
        select(CashTransaction)
        .where(CashTransaction.account_id == account_id)
        .order_by(CashTransaction.created_at.desc(), CashTransaction.id.desc())
    )
    return db.scalars(newest_first).all()


@router.post(
    "/{account_id}/transactions",
    response_model=TransactionOut,
    status_code=status.HTTP_201_CREATED,
)
def add_transaction(
    account_id: int,
    data: TransactionIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cash.record_transaction(db, get_owned(db, CashAccount, account_id, user), data)
