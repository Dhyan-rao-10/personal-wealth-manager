import os
import tempfile

import pytest

# Point the app at a throwaway database before app.config is imported,
# so tests never touch the real wealth.db.
_test_db = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db}"

from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402

PASSWORD = "correct-horse-battery"


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def make_user(client):
    """Registers a user, logs them in, and returns headers for their requests."""

    def _make_user(email="asha@example.com", name="Asha"):
        details = {"name": name, "email": email, "password": PASSWORD}
        assert client.post("/api/auth/register", json=details).status_code == 201
        login = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
        return {"Authorization": f"Bearer {login.json()['token']}"}

    return _make_user


@pytest.fixture
def user(make_user):
    return make_user()
