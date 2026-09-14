import os
from datetime import date
import joblib
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.queue_entry import QueueEntry
from app.models.doctor import Doctor
from app.models.department import Department
from app.models.model_prediction import ModelPrediction
from app.models.user import User
from app.models.enums import UserRole

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XGB_MODEL_PATH = os.path.join(BASE_DIR, "ml", "models", "xgboost_wait_time.joblib")
LSTM_MODEL_PATH = os.path.join(BASE_DIR, "ml", "models", "lstm_demand_forecast.joblib")
_xgb_artifact = None
_lstm_artifact = None


def load_xgb_model():
    global _xgb_artifact
    if _xgb_artifact is None:
        _xgb_artifact = joblib.load(XGB_MODEL_PATH) if os.path.exists(XGB_MODEL_PATH) else None
    return _xgb_artifact


def load_lstm_model():
    global _lstm_artifact
    if _lstm_artifact is None:
        _lstm_artifact = joblib.load(LSTM_MODEL_PATH) if os.path.exists(LSTM_MODEL_PATH) else None
    return _lstm_artifact


def _authorized_queue_entry(db: Session, queue_entry_id: int, user: User) -> QueueEntry:
    entry = db.query(QueueEntry).filter(QueueEntry.id == queue_entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    if user.role != UserRole.SUPER_ADMIN and entry.organization_id != user.organization_id:
        raise HTTPException(status_code=403, detail="You do not have access to this hospital")
    if user.role == UserRole.PATIENT and (not user.patient_profile or entry.patient_id != user.patient_profile.id):
        raise HTTPException(status_code=403, detail="You do not have permission to access this prediction")
    if user.role == UserRole.DOCTOR and (not user.doctor_profile or entry.doctor_id != user.doctor_profile.id):
        raise HTTPException(status_code=403, detail="You do not have permission to access this prediction")
    return entry


def predict_waiting_time(db: Session, queue_entry_id: int, user: User) -> float:
    q_entry = _authorized_queue_entry(db, queue_entry_id, user)
    queue_length = db.query(func.count(QueueEntry.id)).filter(
        QueueEntry.organization_id == q_entry.organization_id,
        QueueEntry.department_id == q_entry.department_id,
        QueueEntry.queue_date == date.today(),
    ).scalar() or 0
    doctors_available = db.query(func.count(Doctor.id)).filter(
        Doctor.organization_id == q_entry.organization_id,
        Doctor.department_id == q_entry.department_id,
        Doctor.is_available == True,
    ).scalar() or 0
    avg_consultation = db.query(func.avg(Doctor.consultation_duration)).filter(
        Doctor.organization_id == q_entry.organization_id,
        Doctor.department_id == q_entry.department_id,
    ).scalar() or 15.0

    artifact = load_xgb_model()
    if artifact and "model" in artifact:
        priority_map = {"NORMAL": 0, "URGENT": 1, "EMERGENCY": 2}
        app_type_map = {"WALK_IN": 0, "APPOINTMENT": 1, "FOLLOW_UP": 2}
        features = pd.DataFrame([{
            "department_id": q_entry.department_id,
            "priority_encoded": priority_map.get(q_entry.priority.value, 0),
            "app_type_encoded": app_type_map.get(q_entry.appointment.appointment_type if q_entry.appointment else "WALK_IN", 0),
            "queue_length": queue_length,
            "doctors_available": doctors_available,
            "avg_consultation_minutes": float(avg_consultation),
            "recent_arrivals_30m": queue_length,
            "recent_completions_30m": 0,
            "hour": q_entry.check_in_time.hour if q_entry.check_in_time else 10,
            "day_of_week": q_entry.check_in_time.weekday() if q_entry.check_in_time else 0,
        }])
        pred_val = max(2.0, round(float(artifact["model"].predict(features)[0]), 1))
    else:
        pred_val = max(2.0, round((queue_length * float(avg_consultation)) / max(1, doctors_available), 1))

    db.add(ModelPrediction(model_name="XGBoost_WaitTime", model_version="v1.0.0-xgboost", department_id=q_entry.department_id, queue_entry_id=q_entry.id, prediction_value=pred_val, prediction_unit="minutes"))
    q_entry.predicted_wait_minutes = pred_val
    db.commit()
    return pred_val


def forecast_department_demand(db: Session, department_id: int, horizon_hours: int = 6, user: User | None = None) -> dict:
    if horizon_hours not in {1, 6, 12, 24}:
        raise HTTPException(status_code=422, detail="Horizon must be 1, 6, 12, or 24 hours")
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    if user and user.role != UserRole.SUPER_ADMIN and dept.organization_id != user.organization_id:
        raise HTTPException(status_code=403, detail="You do not have access to this hospital")

    multiplier = horizon_hours / 6.0
    arrivals_now = db.query(func.count(QueueEntry.id)).filter(QueueEntry.department_id == department_id, QueueEntry.queue_date == date.today()).scalar() or 0
    predicted_arrivals = max(1, int((arrivals_now or 18) * multiplier))
    predicted_queue_depth = max(0, int(predicted_arrivals * 0.66))
    rec_doctors = max(1, int((predicted_arrivals + 4) / 5))
    sequence = [{"hour_ahead": h, "expected_arrivals": max(1, int(predicted_arrivals / horizon_hours)), "expected_queue": int(predicted_queue_depth * h / horizon_hours)} for h in range(1, horizon_hours + 1)]
    return {"department_id": department_id, "horizon_hours": horizon_hours, "predicted_arrivals": predicted_arrivals, "predicted_queue_depth": predicted_queue_depth, "recommended_doctor_capacity": rec_doctors, "forecast_sequence": sequence}
