"""Makes a registered user an administrator: python -m app.make_admin someone@example.com"""
import sys

from sqlalchemy import select

from app import models  # noqa: F401  (importing models registers the tables)
from app.database import SessionLocal
from app.models.user import User


def make_admin(email: str) -> bool:
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email.lower()))
        if user is None:
            return False
        user.is_admin = True
        db.commit()
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m app.make_admin someone@example.com")
    if not make_admin(sys.argv[1]):
        sys.exit("No user has that email. Register first, then run this again.")
    print(f"{sys.argv[1]} is now an administrator.")
