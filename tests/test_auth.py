import logging
from datetime import timedelta

from sqlalchemy import select

from app.models.user import User, UserSession, utcnow
from tests.conftest import PASSWORD

ASHA = {"name": "Asha", "email": "asha@example.com", "password": PASSWORD}


def test_tc_auth_01_register_creates_an_account(client):
    res = client.post("/api/auth/register", json=ASHA)
    assert res.status_code == 201
    assert res.json()["email"] == "asha@example.com"
    assert "password" not in res.text


def test_tc_auth_01_duplicate_email_is_rejected(client):
    client.post("/api/auth/register", json=ASHA)
    res = client.post("/api/auth/register", json={**ASHA, "email": "ASHA@example.com"})
    assert res.status_code == 409


def test_tc_auth_02_correct_details_return_a_token(client):
    client.post("/api/auth/register", json=ASHA)
    res = client.post("/api/auth/login", json={"email": ASHA["email"], "password": PASSWORD})
    assert res.status_code == 200
    assert res.json()["token"]


def test_tc_auth_02_wrong_details_get_the_same_generic_401(client):
    client.post("/api/auth/register", json=ASHA)
    wrong_password = client.post(
        "/api/auth/login", json={"email": ASHA["email"], "password": "not-the-password"}
    )
    unknown_email = client.post(
        "/api/auth/login", json={"email": "nobody@example.com", "password": PASSWORD}
    )
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()


def test_tc_auth_03_logout_ends_the_session(client, user):
    assert client.post("/api/auth/logout", headers=user).status_code == 204
    assert client.get("/api/auth/me", headers=user).status_code == 401


def test_tc_auth_03_session_expires(client, user, db):
    session = db.scalars(select(UserSession)).one()
    session.expires_at = utcnow() - timedelta(seconds=1)
    db.commit()
    assert client.get("/api/auth/me", headers=user).status_code == 401


def test_tc_sec_01_passwords_are_salted_hashes(client, db):
    client.post("/api/auth/register", json=ASHA)
    client.post("/api/auth/register", json={**ASHA, "email": "ravi@example.com"})
    first, second = db.scalars(select(User)).all()
    assert PASSWORD not in first.password_hash
    assert first.password_hash.startswith("scrypt$")
    assert first.password_hash != second.password_hash


def test_tc_sec_02_no_session_gets_401(client):
    assert client.get("/api/auth/me").status_code == 401
    fake = {"Authorization": "Bearer made-up"}
    assert client.get("/api/auth/me", headers=fake).status_code == 401


def test_tc_sec_04_account_locks_after_five_failures(client, db, caplog):
    client.post("/api/auth/register", json=ASHA)
    wrong = {"email": ASHA["email"], "password": "not-the-password"}
    with caplog.at_level(logging.WARNING, logger="pwm.audit"):
        for _ in range(5):
            assert client.post("/api/auth/login", json=wrong).status_code == 401
    correct = {"email": ASHA["email"], "password": PASSWORD}
    assert client.post("/api/auth/login", json=correct).status_code == 423
    assert "account_locked" in caplog.text

    locked = db.scalars(select(User)).one()
    locked.locked_until = utcnow() - timedelta(seconds=1)
    db.commit()
    assert client.post("/api/auth/login", json=correct).status_code == 200


def test_tc_sec_05_invalid_input_returns_422(client):
    assert client.post("/api/auth/register", json={**ASHA, "email": "nope"}).status_code == 422
    assert client.post("/api/auth/register", json={**ASHA, "password": "short"}).status_code == 422


def test_tc_sec_05_sql_injection_has_no_effect(client):
    payload = {"email": "x@example.com", "password": "' OR '1'='1"}
    assert client.post("/api/auth/login", json=payload).status_code == 401


def test_tc_sec_06_secrets_never_reach_the_logs(client, caplog):
    with caplog.at_level(logging.DEBUG):
        client.post("/api/auth/register", json=ASHA)
        login = client.post(
            "/api/auth/login", json={"email": ASHA["email"], "password": PASSWORD}
        )
        client.get("/api/auth/me", headers={"Authorization": f"Bearer {login.json()['token']}"})
    assert PASSWORD not in caplog.text
    assert login.json()["token"] not in caplog.text
