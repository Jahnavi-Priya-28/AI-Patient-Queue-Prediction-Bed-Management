from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.domain import DoctorResponse
from app.services.doctors import get_all_doctors

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("", response_model=List[DoctorResponse])
def list_doctors(department_id: Optional[int] = None, db: Session = Depends(get_db)):
    """List doctors, optionally filtered by department."""
    return get_all_doctors(db, department_id)
