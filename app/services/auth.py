"""Registration, login and sessions."""
import logging
from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import LOCK_MINUTES, MAX_FAILED_LOGINS, SESSION_MINUTES
from app.models.user import User, UserSession, utcnow
from app.schemas.auth import LoginRequest, RegisterRequest
from app.security import hash_password, hash_token, new_token, verify_password

audit = logging.getLogger("pwm.audit")


def register(db: Session, data: RegisterRequest) -> User:
    email = data.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "That email is already registered")
    user = User(name=data.name, email=email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    return user


def login(db: Session, data: LoginRequest) -> str:
    wrong_details = HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong email or password")
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if user is None:
        raise wrong_details
    if user.locked_until and user.locked_until > utcnow():
        raise HTTPException(status.HTTP_423_LOCKED, "Account locked. Try again later")
    if not verify_password(data.password, user.password_hash):
        _record_failure(db, user)
        raise wrong_details
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This account has been deactivated")

    user.failed_logins = 0
    user.locked_until = None
    token = new_token()
    expires_at = utcnow() + timedelta(minutes=SESSION_MINUTES)
    db.add(UserSession(token_hash=hash_token(token), user_id=user.id, expires_at=expires_at))
    db.commit()
    return token


def _record_failure(db: Session, user: User) -> None:
    user.failed_logins += 1
    if user.failed_logins >= MAX_FAILED_LOGINS:
        user.failed_logins = 0
        user.locked_until = utcnow() + timedelta(minutes=LOCK_MINUTES)
        audit.warning("account_locked user_id=%s", user.id)
    db.commit()


def logout(db: Session, token: str) -> None:
    session = db.get(UserSession, hash_token(token))
    if session is not None:
        db.delete(session)
        db.commit()
