RING = {
    "description": "Wedding ring",
    "form": "jewellery",
    "weight_grams": "10.000",
    "purity": "22K",
    "purchase_date": "2021-05-01",
    "purchase_price": "50000.00",
}
URL = "/api/gold"


def test_tc_gold_01_add_holding(client, user):
    res = client.post(URL, json=RING, headers=user)
    assert res.status_code == 201
    assert len(client.get(URL, headers=user).json()) == 1


def test_tc_gold_01_zero_or_negative_weight_is_rejected(client, user):
    for weight in ("0", "-5"):
        res = client.post(URL, json={**RING, "weight_grams": weight}, headers=user)
        assert res.status_code == 422


def test_tc_gold_02_edit_and_delete_holding(client, user):
    item = client.post(URL, json=RING, headers=user).json()
    edited = client.put(f"{URL}/{item['id']}", json={**RING, "form": "coin"}, headers=user)
    assert edited.json()["form"] == "coin"
    assert client.delete(f"{URL}/{item['id']}", headers=user).status_code == 204
    assert client.get(URL, headers=user).json() == []


def test_tc_gold_03_valued_from_the_gold_price(client, user):
    client.post(URL, json=RING, headers=user)
    client.put(f"{URL}/price", json={"price_per_gram": "10000"}, headers=user)
    assert client.get(URL, headers=user).json()[0]["current_value"] == "91666.67"


def test_tc_gold_03_valued_at_purchase_price_until_a_price_is_set(client, user):
    item = client.post(URL, json=RING, headers=user).json()
    assert item["current_value"] == "50000.00"
    assert client.get(f"{URL}/price", headers=user).json()["price_per_gram"] is None


def test_tc_gold_03_updating_the_price_replaces_the_old_one(client, user):
    client.put(f"{URL}/price", json={"price_per_gram": "9000"}, headers=user)
    client.put(f"{URL}/price", json={"price_per_gram": "9500"}, headers=user)
    assert client.get(f"{URL}/price", headers=user).json()["price_per_gram"] == "9500.00"


def test_tc_sec_03_cannot_touch_another_users_gold(client, user, make_user):
    item = client.post(URL, json=RING, headers=user).json()
    other = make_user("ravi@example.com")
    assert client.get(URL, headers=other).json() == []
    assert client.put(f"{URL}/{item['id']}", json=RING, headers=other).status_code == 404
    assert client.delete(f"{URL}/{item['id']}", headers=other).status_code == 404
