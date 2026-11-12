"""Shared request checks: who is calling, and do they own the record they asked for."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserSession, utcnow
from app.security import hash_token

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(status.HTTP_401_UNAUTHORIZED, "Please log in")
    if credentials is None:
        raise unauthorized
    session = db.get(UserSession, hash_token(credentials.credentials))
    if session is None or session.expires_at <= utcnow():
        raise unauthorized
    user = db.get(User, session.user_id)
    if user is None or not user.is_active:
        raise unauthorized
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Administrators only")
    return user


def get_owned(db: Session, model, record_id: int, user: User):
    """Fetches a record owned by this user. Someone else's record looks like it doesn't exist."""
    record = db.get(model, record_id)
    if record is None or record.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    return record
