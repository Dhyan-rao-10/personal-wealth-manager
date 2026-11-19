"""Brings the four asset classes together: net worth, allocation, history and export."""
import csv
import io
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.snapshot import NetWorthSnapshot
from app.money import round_money
from app.services import cash, gold, real_estate, stocks

ASSET_CLASSES = {
    "Real Estate": real_estate.holdings,
    "Gold": gold.holdings,
    "Stocks": stocks.holdings,
    "Cash": cash.holdings,
}


def _shares(totals: dict[str, Decimal], net_worth: Decimal) -> list[dict]:
    percents = {name: Decimal("0.00") for name in totals}
    if net_worth:
        percents = {name: round_money(total / net_worth * 100) for name, total in totals.items()}
        # Rounding can leave the total at 99.99 or 100.01; the largest class absorbs the difference.
        largest = max(totals, key=totals.get)
        percents[largest] += Decimal("100.00") - sum(percents.values())
    return [
        {"name": name, "value": round_money(total), "percent": percents[name]}
        for name, total in totals.items()
    ]


def summary(db: Session, user_id: int) -> dict:
    totals = {
        name: sum((value for _, value in holdings(db, user_id)), Decimal("0"))
        for name, holdings in ASSET_CLASSES.items()
    }
    net_worth = sum(totals.values(), Decimal("0"))
    return {"net_worth": round_money(net_worth), "asset_classes": _shares(totals, net_worth)}


def save_snapshot(db: Session, user_id: int, net_worth: Decimal) -> None:
    """Keeps one snapshot per day. Opening the dashboard again updates today's figure."""
    today = date.today()
    snapshot = db.scalar(
        select(NetWorthSnapshot).where(
            NetWorthSnapshot.user_id == user_id, NetWorthSnapshot.date == today
        )
    )
    if snapshot:
        snapshot.net_worth = net_worth
    else:
        db.add(NetWorthSnapshot(user_id=user_id, date=today, net_worth=net_worth))
    db.commit()


def history(db: Session, user_id: int) -> list[NetWorthSnapshot]:
    oldest_first = (
        select(NetWorthSnapshot)
        .where(NetWorthSnapshot.user_id == user_id)
        .order_by(NetWorthSnapshot.date)
    )
    return list(db.scalars(oldest_first))


def _safe_cell(text: str) -> str:
    """Stops spreadsheet apps treating a saved name as a formula."""
    return f"'{text}" if text.startswith(("=", "+", "-", "@")) else text


def export_csv(db: Session, user_id: int) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Asset class", "Name", "Current value (INR)"])
    for asset_class, holdings in ASSET_CLASSES.items():
        for name, value in holdings(db, user_id):
            writer.writerow([asset_class, _safe_cell(name), round_money(value)])
    return output.getvalue()
