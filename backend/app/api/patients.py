from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.domain import PatientResponse
from app.services.patients import get_all_patients
from app.core.security import require_role
from app.models.enums import UserRole

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("", response_model=List[PatientResponse])
def list_patients(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _user=Depends(require_role([UserRole.RECEPTIONIST, UserRole.ADMIN, UserRole.DOCTOR])),
):
    """Search & list patients (Staff roles only)."""
    return get_all_patients(db, search)
