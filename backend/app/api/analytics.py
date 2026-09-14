from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.domain import DashboardMetricsResponse
from app.services.analytics import get_dashboard_metrics
from app.core.security import require_role
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics & Dashboard Metrics"])


@router.get("/dashboard-metrics", response_model=DashboardMetricsResponse)
def get_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN, UserRole.RECEPTIONIST, UserRole.DOCTOR])),
):
    """Fetch live aggregated operational metrics inside the caller's authorized scope."""
    return get_dashboard_metrics(db, current_user)
