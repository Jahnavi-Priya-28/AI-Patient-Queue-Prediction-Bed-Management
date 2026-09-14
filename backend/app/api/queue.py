from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.domain import QueueEntryResponse, CheckInRequest
from app.services.queue import check_in_patient, call_next_patient, start_consultation, complete_consultation, get_live_queue
from app.services.ml import predict_waiting_time
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.enums import UserRole

router = APIRouter(prefix="/queue", tags=["Queue Management"])


@router.post("/check-in", response_model=QueueEntryResponse, status_code=status.HTTP_201_CREATED)
def check_in(req: CheckInRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q_entry = check_in_patient(db, req, current_user)
    predict_waiting_time(db, q_entry.id, current_user)
    db.refresh(q_entry)
    return q_entry


@router.post("/call-next", response_model=QueueEntryResponse)
def call_next(db: Session = Depends(get_db), current_user: User = Depends(require_role([UserRole.DOCTOR]))):
    return call_next_patient(db, doctor_user_id=current_user.id)


@router.post("/{queue_entry_id}/start-consultation", response_model=QueueEntryResponse)
def start_session(queue_entry_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role([UserRole.DOCTOR, UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN]))):
    return start_consultation(db, queue_entry_id, current_user)


@router.post("/{queue_entry_id}/complete-consultation", response_model=QueueEntryResponse)
def complete_session(queue_entry_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role([UserRole.DOCTOR, UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN]))):
    return complete_consultation(db, queue_entry_id, current_user)


@router.get("", response_model=List[QueueEntryResponse])
def get_queue(department_id: Optional[int] = None, doctor_id: Optional[int] = None, queue_date: Optional[date] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_live_queue(db, current_user, department_id, doctor_id, queue_date)

