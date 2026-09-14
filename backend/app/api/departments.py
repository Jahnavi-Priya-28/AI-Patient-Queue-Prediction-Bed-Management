from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.domain import DepartmentResponse, DepartmentCreate
from app.services.departments import get_all_departments, create_department
from app.core.security import get_current_user, require_role
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("", response_model=List[DepartmentResponse])
def list_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List active hospital departments in the caller's organization."""
    return get_all_departments(db, current_user)


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def add_department(
    req: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN])),
):
    """Create a department in the caller's authorized hospital scope."""
    return create_department(db, req, current_user)
