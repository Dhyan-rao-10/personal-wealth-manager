import logging

from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.user import User, UserSession

audit = logging.getLogger("pwm.audit")


def set_active(db: Session, admin: User, user_id: int, active: bool) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    if user.id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You can't change your own account")
    user.is_active = active
    if not active:
        db.execute(delete(UserSession).where(UserSession.user_id == user.id))
    db.commit()
    event = "account_reactivated" if active else "account_deactivated"
    audit.info("%s user_id=%s by_admin_id=%s", event, user.id, admin.id)
    return user
