from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardOut, SnapshotOut
from app.services import dashboard

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def get_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    summary = dashboard.summary(db, user.id)
    dashboard.save_snapshot(db, user.id, summary["net_worth"])
    return summary


@router.get("/history", response_model=list[SnapshotOut])
def get_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return dashboard.history(db, user.id)


@router.get("/export.csv")
def export_holdings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return Response(
        dashboard.export_csv(db, user.id),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="holdings.csv"'},
    )
