import logging

from app.make_admin import make_admin
from tests.conftest import PASSWORD

URL = "/api/admin/users"


def test_tc_admin_01_list_shows_users_and_no_financial_data(client, user, make_user):
    admin = make_user("admin@example.com", "Admin")
    make_admin("admin@example.com")
    res = client.get(URL, headers=admin)
    assert res.status_code == 200
    assert sorted(u["email"] for u in res.json()) == ["admin@example.com", "asha@example.com"]
    assert set(res.json()[0]) == {"id", "name", "email", "is_active", "is_admin"}


def test_tc_admin_02_deactivated_user_cannot_log_in(client, user, make_user, caplog):
    admin = make_user("admin@example.com", "Admin")
    make_admin("admin@example.com")
    target = next(u for u in client.get(URL, headers=admin).json() if u["name"] == "Asha")
    login = {"email": target["email"], "password": PASSWORD}

    with caplog.at_level(logging.INFO, logger="pwm.audit"):
        assert client.post(f"{URL}/{target['id']}/deactivate", headers=admin).status_code == 200
    assert "account_deactivated" in caplog.text
    assert client.post("/api/auth/login", json=login).status_code == 403
    assert client.get("/api/auth/me", headers=user).status_code == 401

    with caplog.at_level(logging.INFO, logger="pwm.audit"):
        assert client.post(f"{URL}/{target['id']}/reactivate", headers=admin).status_code == 200
    assert "account_reactivated" in caplog.text
    assert client.post("/api/auth/login", json=login).status_code == 200


def test_admin_cannot_deactivate_themselves(client, make_user):
    admin = make_user("admin@example.com", "Admin")
    make_admin("admin@example.com")
    own_id = client.get("/api/auth/me", headers=admin).json()["id"]
    assert client.post(f"{URL}/{own_id}/deactivate", headers=admin).status_code == 400


def test_unknown_user_returns_404(client, make_user):
    admin = make_user("admin@example.com", "Admin")
    make_admin("admin@example.com")
    assert client.post(f"{URL}/99999/deactivate", headers=admin).status_code == 404


def test_make_admin_reports_an_unknown_email(client):
    assert make_admin("nobody@example.com") is False


def test_tc_sec_02_non_admin_gets_403(client, user):
    assert client.get(URL, headers=user).status_code == 403
    assert client.post(f"{URL}/1/deactivate", headers=user).status_code == 403


def test_tc_sec_02_no_session_gets_401(client):
    assert client.get(URL).status_code == 401
