import csv
import io
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.models.snapshot import NetWorthSnapshot
from app.services.dashboard import _shares
from tests.test_cash import SAVINGS
from tests.test_gold import RING
from tests.test_real_estate import HOUSE
from tests.test_stocks import INFY

URL = "/api/dashboard"


def add_one_of_each(client, headers):
    client.post("/api/real-estate", json=HOUSE, headers=headers)
    client.post("/api/gold", json=RING, headers=headers)
    client.put("/api/gold/price", json={"price_per_gram": "10000"}, headers=headers)
    client.post("/api/stocks", json=INFY, headers=headers)
    client.post("/api/cash", json=SAVINGS, headers=headers)


def test_tc_dash_01_net_worth_is_the_sum_of_all_classes(client, user):
    add_one_of_each(client, user)
    data = client.get(URL, headers=user).json()
    # 60,00,000 + 91,666.67 + 1,000 + 1,000
    assert data["net_worth"] == "6093666.67"


def test_tc_dash_01_new_user_has_zero_net_worth(client, user):
    data = client.get(URL, headers=user).json()
    assert data["net_worth"] == "0.00"
    assert [item["percent"] for item in data["asset_classes"]] == ["0.00"] * 4


def test_tc_dash_02_shares_add_up(client, user):
    add_one_of_each(client, user)
    classes = client.get(URL, headers=user).json()["asset_classes"]
    assert sum(Decimal(item["value"]) for item in classes) == Decimal("6093666.67")
    assert sum(Decimal(item["percent"]) for item in classes) == Decimal("100.00")


def test_tc_dash_02_rounding_still_adds_up_to_100(db):
    equal = {"A": Decimal("1"), "B": Decimal("1"), "C": Decimal("1")}
    shares = _shares(equal, Decimal("3"))
    assert sum(item["percent"] for item in shares) == Decimal("100.00")


def test_tc_dash_03_one_snapshot_a_day(client, user, db):
    client.get(URL, headers=user)
    client.get(URL, headers=user)
    assert len(db.scalars(select(NetWorthSnapshot)).all()) == 1


def test_tc_dash_03_history_is_oldest_first(client, user, db):
    client.get(URL, headers=user)
    today = db.scalars(select(NetWorthSnapshot)).one()
    yesterday = today.date - timedelta(days=1)
    db.add(NetWorthSnapshot(user_id=today.user_id, date=yesterday, net_worth=Decimal("5.00")))
    db.commit()
    dates = [item["date"] for item in client.get(f"{URL}/history", headers=user).json()]
    assert dates == [yesterday.isoformat(), date.today().isoformat()]


def test_tc_dash_04_csv_has_one_row_per_holding(client, user):
    add_one_of_each(client, user)
    res = client.get(f"{URL}/export.csv", headers=user)
    assert res.headers["content-type"].startswith("text/csv")
    rows = list(csv.DictReader(io.StringIO(res.text)))
    assert [row["Asset class"] for row in rows] == ["Real Estate", "Gold", "Stocks", "Cash"]
    assert rows[1]["Current value (INR)"] == "91666.67"


def test_tc_dash_04_csv_neutralises_formulas(client, user):
    client.post("/api/cash", json={**SAVINGS, "name": "=HYPERLINK(1)"}, headers=user)
    assert "'=HYPERLINK(1)" in client.get(f"{URL}/export.csv", headers=user).text


def test_tc_sec_03_dashboard_shows_only_your_own_data(client, user, make_user):
    add_one_of_each(client, user)
    other = make_user("ravi@example.com")
    assert client.get(URL, headers=other).json()["net_worth"] == "0.00"
    assert len(client.get(f"{URL}/export.csv", headers=other).text.splitlines()) == 1
