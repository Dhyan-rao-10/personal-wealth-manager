HOUSE = {
    "name": "Koramangala flat",
    "type": "residential",
    "location": "Bengaluru",
    "purchase_date": "2020-01-15",
    "purchase_price": "5000000.00",
    "current_value": "6000000.00",
}
URL = "/api/real-estate"


def test_tc_re_01_add_property(client, user):
    res = client.post(URL, json=HOUSE, headers=user)
    assert res.status_code == 201
    assert [p["name"] for p in client.get(URL, headers=user).json()] == [HOUSE["name"]]


def test_tc_re_01_missing_field_or_negative_amount_is_rejected(client, user):
    missing = {key: value for key, value in HOUSE.items() if key != "location"}
    assert client.post(URL, json=missing, headers=user).status_code == 422
    negative = {**HOUSE, "current_value": "-1"}
    assert client.post(URL, json=negative, headers=user).status_code == 422


def test_tc_re_02_edit_and_delete_property(client, user):
    item = client.post(URL, json=HOUSE, headers=user).json()
    edited = client.put(f"{URL}/{item['id']}", json={**HOUSE, "name": "New name"}, headers=user)
    assert edited.json()["name"] == "New name"
    assert client.delete(f"{URL}/{item['id']}", headers=user).status_code == 204
    assert client.get(URL, headers=user).json() == []


def test_tc_re_03_gain_shown_in_rupees_and_percent(client, user):
    item = client.post(URL, json=HOUSE, headers=user).json()
    assert item["gain_loss"] == "1000000.00"
    assert item["gain_loss_percent"] == "20.00"


def test_tc_sec_03_cannot_touch_another_users_property(client, user, make_user):
    item = client.post(URL, json=HOUSE, headers=user).json()
    other = make_user("ravi@example.com")
    assert client.get(URL, headers=other).json() == []
    assert client.put(f"{URL}/{item['id']}", json=HOUSE, headers=other).status_code == 404
    assert client.delete(f"{URL}/{item['id']}", headers=other).status_code == 404


def test_tc_sec_05_script_in_a_name_is_stored_as_plain_text(client, user):
    payload = {**HOUSE, "name": "<script>alert(1)</script>"}
    assert client.post(URL, json=payload, headers=user).json()["name"] == payload["name"]
