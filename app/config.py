import os
from pathlib import Path

APP_NAME = "Personal Wealth Manager"
APP_VERSION = "1.0.0"

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# SQLite file in the project folder by default; override with the DATABASE_URL env var.
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(PROJECT_ROOT / 'wealth.db').as_posix()}")

SESSION_MINUTES = 60
MAX_FAILED_LOGINS = 5
LOCK_MINUTES = 15

# Set FORCE_HTTPS=1 when deployed so plain HTTP requests are redirected to HTTPS.
FORCE_HTTPS = os.getenv("FORCE_HTTPS") == "1"
