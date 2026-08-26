from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.department import Department
from app.schemas.domain import DepartmentCreate


def get_all_departments(db: Session) -> List[Department]:
    return db.query(Department).order_by(Department.name).all()


def create_department(db: Session, req: DepartmentCreate) -> Department:
    existing = db.query(Department).filter(
        (Department.name == req.name) | (Department.code == req.code.upper())
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department name or code already exists",
        )
    dept = Department(name=req.name, code=req.code.upper(), description=req.description, active=True)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept
