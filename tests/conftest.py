import os
import tempfile

import pytest

# Point the app at a throwaway database before app.config is imported,
# so tests never touch the real wealth.db.
_test_db = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db}"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
