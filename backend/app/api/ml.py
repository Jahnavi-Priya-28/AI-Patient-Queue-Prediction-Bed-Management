from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.domain import PredictWaitingTimeRequest, PredictWaitingTimeResponse, ForecastDemandRequest, ForecastDemandResponse
from app.services.ml import predict_waiting_time, forecast_department_demand
from app.core.security import require_role
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter(prefix="/ml", tags=["Machine Learning Inference"])


@router.post("/predict-waiting-time", response_model=PredictWaitingTimeResponse)
def predict_wait_endpoint(
    req: PredictWaitingTimeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.PATIENT, UserRole.DOCTOR, UserRole.RECEPTIONIST, UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN])),
):
    """Run the XGBoost prediction only for an authorized queue entry."""
    wait_mins = predict_waiting_time(db, req.queue_entry_id, current_user)
    return PredictWaitingTimeResponse(queue_entry_id=req.queue_entry_id, predicted_wait_minutes=wait_mins)


@router.post("/forecast", response_model=ForecastDemandResponse)
def forecast_demand_endpoint(
    req: ForecastDemandRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.DOCTOR, UserRole.RECEPTIONIST, UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN])),
):
    """Run the LSTM forecast for a department in the user's authorized organization."""
    return forecast_department_demand(db, req.department_id, req.horizon_hours, current_user)
