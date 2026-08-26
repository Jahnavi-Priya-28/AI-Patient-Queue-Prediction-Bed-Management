from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.domain import (
    PredictWaitingTimeRequest,
    PredictWaitingTimeResponse,
    ForecastDemandRequest,
    ForecastDemandResponse,
)
from app.services.ml import predict_waiting_time, forecast_department_demand

router = APIRouter(prefix="/ml", tags=["Machine Learning Inference"])


@router.post("/predict-waiting-time", response_model=PredictWaitingTimeResponse)
def predict_wait_endpoint(req: PredictWaitingTimeRequest, db: Session = Depends(get_db)):
    """Run XGBoost model regression to predict patient queue waiting time."""
    wait_mins = predict_waiting_time(db, req.queue_entry_id)
    return PredictWaitingTimeResponse(
        queue_entry_id=req.queue_entry_id,
        predicted_wait_minutes=wait_mins,
    )


@router.post("/forecast", response_model=ForecastDemandResponse)
def forecast_demand_endpoint(req: ForecastDemandRequest, db: Session = Depends(get_db)):
    """Run LSTM model to forecast multivariate department arrival demand."""
    return forecast_department_demand(db, req.department_id, req.horizon_hours)
