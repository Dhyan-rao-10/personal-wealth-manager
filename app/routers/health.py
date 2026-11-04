from fastapi import APIRouter

from app.config import APP_VERSION

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok", "version": APP_VERSION}
