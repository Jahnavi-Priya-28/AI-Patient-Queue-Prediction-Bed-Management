from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.department import Department
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.domain import DepartmentCreate


def _org_filter_for(user: User) -> Optional[int]:
    return None if user.role == UserRole.SUPER_ADMIN else user.organization_id


def get_all_departments(db: Session, user: User) -> List[Department]:
    query = db.query(Department)
    organization_id = _org_filter_for(user)
    if organization_id is not None:
        query = query.filter(Department.organization_id == organization_id)
    return query.order_by(Department.name).all()


def create_department(db: Session, req: DepartmentCreate, user: User) -> Department:
    organization_id = _org_filter_for(user) or user.organization_id
    if not organization_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hospital organization is required")
    existing = db.query(Department).filter(
        Department.organization_id == organization_id,
        ((Department.name == req.name) | (Department.code == req.code.upper())),
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Department name or code already exists in this hospital")
    dept = Department(organization_id=organization_id, name=req.name, code=req.code.upper(), description=req.description, active=True)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept
