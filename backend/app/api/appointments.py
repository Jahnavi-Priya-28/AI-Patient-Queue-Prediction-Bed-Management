from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.domain import AppointmentResponse, AppointmentCreate
from app.services.appointments import create_appointment, get_appointments
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def book_appointment(
    req: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Book a new patient appointment."""
    return create_appointment(db, current_user.id, req)


@router.get("", response_model=List[AppointmentResponse])
def list_appointments(
    appt_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List appointments scoped by user role."""
    if current_user.role == "PATIENT":
        return get_appointments(db, patient_user_id=current_user.id, appt_date=appt_date)
    elif current_user.role == "DOCTOR":
        return get_appointments(db, doctor_user_id=current_user.id, appt_date=appt_date)
    else:
        return get_appointments(db, appt_date=appt_date)
