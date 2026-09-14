from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.enums import UserRole
from app.models.patient import Patient
from app.models.user import User


def get_all_patients(db: Session, user: User, search: Optional[str] = None) -> List[dict]:
    query = db.query(Patient).options(joinedload(Patient.user))
    if user.role != UserRole.SUPER_ADMIN:
        query = query.filter(Patient.organization_id == user.organization_id)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Patient.patient_number.ilike(search_pattern)) |
            (Patient.user.has(first_name=search_pattern)) |
            (Patient.user.has(last_name=search_pattern)) |
            (Patient.user.has(email=search_pattern))
        )
    patients = query.order_by(Patient.created_at.desc()).all()

    return [{
        "id": p.id,
        "user_id": p.user_id,
        "patient_number": p.patient_number,
        "date_of_birth": p.date_of_birth,
        "gender": p.gender,
        "phone": p.phone,
        "address": p.address,
        "emergency_contact": p.emergency_contact,
        "first_name": p.user.first_name if p.user else "",
        "last_name": p.user.last_name if p.user else "",
        "email": p.user.email if p.user else "",
    } for p in patients]
