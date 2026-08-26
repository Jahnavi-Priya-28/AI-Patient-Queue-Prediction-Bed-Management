from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.schemas.health import HealthCheckResponse
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    """
    System Health Check Endpoint.
    Verifies API status and database connectivity.
    """
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    return HealthCheckResponse(
        status="healthy" if db_connected else "degraded",
        project_name=settings.PROJECT_NAME,
        environment=settings.ENVIRONMENT,
        database_connected=db_connected,
    )
