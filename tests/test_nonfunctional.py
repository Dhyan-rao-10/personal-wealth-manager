import statistics
import time
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.orm import sessionmaker

from app.database import engine
from app.models.cash import CashAccount
from app.models.real_estate import Property
from app.models.user import User

pytestmark = pytest.mark.usefixtures("client")


def test_tc_perf_01_requests_stay_fast_with_1000_holdings(client, user, db):
    owner = db.query(User).one()
    db.add_all(
        Property(
            user_id=owner.id,
            name=f"Plot {number}",
            type="land",
            location="Mysuru",
            purchase_date=date(2020, 1, 1),
            purchase_price=Decimal("100.00"),
            current_value=Decimal("200.00"),
        )
        for number in range(1000)
    )
    db.commit()

    timings = []
    for _ in range(20):
        start = time.perf_counter()
        assert client.get("/api/dashboard", headers=user).status_code == 200
        timings.append(time.perf_counter() - start)
    assert statistics.quantiles(timings, n=20)[-1] <= 0.5


def test_tc_rel_01_saved_data_survives_a_restart(client, user):
    account = {"name": "Wallet", "type": "wallet", "opening_balance": "75.50"}
    client.post("/api/cash", json=account, headers=user)
    engine.dispose()  # drops every open connection, as stopping the app would
    fresh_session = sessionmaker(bind=engine)()
    assert fresh_session.query(CashAccount).one().balance == Decimal("75.50")
    fresh_session.close()


def test_tc_rel_01_failed_save_leaves_no_partial_record(client, user, db):
    owner = db.query(User).one()
    account = CashAccount(
        user_id=owner.id,
        name="Wallet",
        type="wallet",
        opening_balance=Decimal("10.00"),
        balance=Decimal("10.00"),
    )
    db.add(account)
    db.commit()

    account.balance = Decimal("999.00")
    db.flush()
    db.rollback()  # what happens when anything fails before the commit
    db.expire_all()
    assert db.get(CashAccount, account.id).balance == Decimal("10.00")
