from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.domain import DashboardMetricsResponse
from app.services.analytics import get_dashboard_metrics

router = APIRouter(prefix="/analytics", tags=["Analytics & Dashboard Metrics"])


@router.get("/dashboard-metrics", response_model=DashboardMetricsResponse)
def get_metrics(db: Session = Depends(get_db)):
    """Fetch live aggregated PostgreSQL metrics for role-based dashboards."""
    return get_dashboard_metrics(db)
