from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.schemas.admin import AdminUserOut
from app.services import admin as admin_service

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=list[AdminUserOut])
def list_users(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.id)).all()


@router.post("/users/{user_id}/deactivate", response_model=AdminUserOut)
def deactivate(
    user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)
):
    return admin_service.set_active(db, admin, user_id, active=False)


@router.post("/users/{user_id}/reactivate", response_model=AdminUserOut)
def reactivate(
    user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)
):
    return admin_service.set_active(db, admin, user_id, active=True)
