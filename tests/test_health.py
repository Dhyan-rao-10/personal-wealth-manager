from app.config import APP_VERSION


def test_health_returns_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "version": APP_VERSION}


def test_home_page_loads(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "Personal Wealth Manager" in res.text
