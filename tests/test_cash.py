SAVINGS = {"name": "SBI savings", "type": "bank", "opening_balance": "1000.00"}
URL = "/api/cash"


def add_account(client, headers):
    return client.post(URL, json=SAVINGS, headers=headers).json()


def test_tc_cash_01_add_account(client, user):
    account = add_account(client, user)
    assert account["balance"] == "1000.00"


def test_tc_cash_01_negative_opening_balance_is_rejected(client, user):
    res = client.post(URL, json={**SAVINGS, "opening_balance": "-1"}, headers=user)
    assert res.status_code == 422


def test_tc_cash_02_deposit_raises_the_balance(client, user):
    account = add_account(client, user)
    deposit = {"type": "deposit", "amount": "500.00"}
    url = f"{URL}/{account['id']}/transactions"
    assert client.post(url, json=deposit, headers=user).status_code == 201
    assert client.get(URL, headers=user).json()[0]["balance"] == "1500.00"


def test_tc_cash_02_withdrawal_above_balance_is_rejected(client, user):
    account = add_account(client, user)
    withdrawal = {"type": "withdrawal", "amount": "1000.01"}
    url = f"{URL}/{account['id']}/transactions"
    assert client.post(url, json=withdrawal, headers=user).status_code == 400
    assert client.get(URL, headers=user).json()[0]["balance"] == "1000.00"
    assert client.get(url, headers=user).json() == []


def test_tc_cash_03_history_is_newest_first(client, user):
    account = add_account(client, user)
    url = f"{URL}/{account['id']}/transactions"
    client.post(url, json={"type": "deposit", "amount": "1.00", "note": "first"}, headers=user)
    client.post(url, json={"type": "withdrawal", "amount": "1.00", "note": "second"}, headers=user)
    assert [item["note"] for item in client.get(url, headers=user).json()] == ["second", "first"]


def test_deleting_an_account_removes_it(client, user):
    account = add_account(client, user)
    assert client.delete(f"{URL}/{account['id']}", headers=user).status_code == 204
    assert client.get(URL, headers=user).json() == []


def test_tc_sec_03_cannot_touch_another_users_cash(client, user, make_user):
    account = add_account(client, user)
    other = make_user("ravi@example.com")
    url = f"{URL}/{account['id']}/transactions"
    deposit = {"type": "deposit", "amount": "1.00"}
    assert client.get(URL, headers=other).json() == []
    assert client.get(url, headers=other).status_code == 404
    assert client.post(url, json=deposit, headers=other).status_code == 404
    assert client.delete(f"{URL}/{account['id']}", headers=other).status_code == 404
