from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.domain import DepartmentResponse, DepartmentCreate
from app.services.departments import get_all_departments, create_department
from app.core.security import require_role
from app.models.enums import UserRole

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("", response_model=List[DepartmentResponse])
def list_departments(db: Session = Depends(get_db)):
    """List all active hospital departments."""
    return get_all_departments(db)


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def add_department(
    req: DepartmentCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_role([UserRole.ADMIN])),
):
    """Create a new hospital department (Admin only)."""
    return create_department(db, req)
