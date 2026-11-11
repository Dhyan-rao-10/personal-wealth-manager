import importlib
import logging
import pkgutil
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import models, routers  # noqa: F401  (importing models registers the tables)
from app.config import APP_NAME, APP_VERSION, FORCE_HTTPS
from app.database import Base, engine

STATIC_DIR = Path(__file__).parent / "static"

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan)

if FORCE_HTTPS:
    app.add_middleware(HTTPSRedirectMiddleware)

# Every file in app/routers plugs itself in, so a new feature never edits this file.
for module in pkgutil.iter_modules(routers.__path__):
    app.include_router(importlib.import_module(f"app.routers.{module.name}").router)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")
