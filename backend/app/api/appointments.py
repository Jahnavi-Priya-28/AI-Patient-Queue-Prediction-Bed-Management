from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.domain import AppointmentResponse, AppointmentCreate
from app.services.appointments import create_appointment, get_appointments
from app.core.security import get_current_user, require_role
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def book_appointment(req: AppointmentCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role([UserRole.PATIENT]))):
    """Book a new patient appointment in the patient's hospital."""
    return create_appointment(db, current_user, req)


@router.get("", response_model=List[AppointmentResponse])
def list_appointments(appt_date: Optional[date] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List appointments scoped by authenticated role and organization."""
    return get_appointments(db, current_user, appt_date=appt_date)
