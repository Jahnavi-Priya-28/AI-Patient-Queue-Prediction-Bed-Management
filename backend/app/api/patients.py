from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.domain import PatientResponse
from app.services.patients import get_all_patients
from app.core.security import require_role
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("", response_model=List[PatientResponse])
def list_patients(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.RECEPTIONIST, UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN, UserRole.DOCTOR])),
):
    """Search and list patients inside the caller's authorized hospital scope."""
    return get_all_patients(db, current_user, search)
