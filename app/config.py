import os
from pathlib import Path

APP_NAME = "Personal Wealth Manager"
APP_VERSION = "0.1.0"

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# SQLite file in the project folder by default; override with the DATABASE_URL env var.
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(PROJECT_ROOT / 'wealth.db').as_posix()}")
