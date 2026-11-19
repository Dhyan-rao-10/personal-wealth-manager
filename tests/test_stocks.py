INFY = {
    "symbol": "infy",
    "company": "Infosys",
    "exchange": "NSE",
    "quantity": 10,
    "average_buy_price": "100.00",
}
URL = "/api/stocks"


def test_tc_stock_01_add_holding(client, user):
    res = client.post(URL, json=INFY, headers=user)
    assert res.status_code == 201
    assert res.json()["symbol"] == "INFY"


def test_tc_stock_01_zero_or_negative_quantity_is_rejected(client, user):
    for quantity in (0, -3):
        res = client.post(URL, json={**INFY, "quantity": quantity}, headers=user)
        assert res.status_code == 422


def test_tc_stock_02_edit_and_delete_holding(client, user):
    item = client.post(URL, json=INFY, headers=user).json()
    edited = client.put(f"{URL}/{item['id']}", json={**INFY, "quantity": 20}, headers=user)
    assert edited.json()["quantity"] == 20
    assert client.delete(f"{URL}/{item['id']}", headers=user).status_code == 204
    assert client.get(URL, headers=user).json() == []


def test_tc_stock_03_value_and_gain_from_current_price(client, user):
    item = client.post(URL, json=INFY, headers=user).json()
    res = client.put(f"{URL}/{item['id']}/price", json={"current_price": "120"}, headers=user)
    assert res.json()["current_value"] == "1200.00"
    assert res.json()["gain_loss"] == "200.00"
    assert res.json()["gain_loss_percent"] == "20.00"


def test_tc_stock_03_valued_at_buy_price_until_a_price_is_set(client, user):
    item = client.post(URL, json=INFY, headers=user).json()
    assert item["current_value"] == "1000.00"
    assert item["gain_loss"] == "0.00"


def test_tc_sec_03_cannot_touch_another_users_stock(client, user, make_user):
    item = client.post(URL, json=INFY, headers=user).json()
    other = make_user("ravi@example.com")
    price = {"current_price": "1"}
    assert client.get(URL, headers=other).json() == []
    assert client.put(f"{URL}/{item['id']}", json=INFY, headers=other).status_code == 404
    assert client.put(f"{URL}/{item['id']}/price", json=price, headers=other).status_code == 404
    assert client.delete(f"{URL}/{item['id']}", headers=other).status_code == 404
