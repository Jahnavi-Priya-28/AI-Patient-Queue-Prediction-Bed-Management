from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.domain import DoctorResponse
from app.services.doctors import get_all_doctors
from app.core.security import require_role
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("", response_model=List[DoctorResponse])
def list_doctors(
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN, UserRole.RECEPTIONIST, UserRole.DOCTOR, UserRole.PATIENT])),
):
    """List doctors in the authenticated user's organization."""
    return get_all_doctors(db, current_user, department_id)
