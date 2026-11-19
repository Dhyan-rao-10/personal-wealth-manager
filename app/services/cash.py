from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cash import CashAccount, CashTransaction
from app.schemas.cash import TransactionIn


def record_transaction(db: Session, account: CashAccount, data: TransactionIn) -> CashTransaction:
    """Saves the transaction and the new balance together, so they can't disagree."""
    if data.type == "withdrawal" and data.amount > account.balance:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Withdrawal is more than the balance")
    change = data.amount if data.type == "deposit" else -data.amount
    account.balance = account.balance + change
    transaction = CashTransaction(account_id=account.id, **data.model_dump())
    db.add(transaction)
    db.commit()
    return transaction


def holdings(db: Session, user_id: int) -> list[tuple[str, object]]:
    """Each account as (name, balance), used by the dashboard and CSV export."""
    accounts = db.scalars(select(CashAccount).where(CashAccount.user_id == user_id))
    return [(account.name, account.balance) for account in accounts]
