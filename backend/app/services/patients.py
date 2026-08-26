from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.patient import Patient


def get_all_patients(db: Session, search: Optional[str] = None) -> List[dict]:
    query = db.query(Patient).options(joinedload(Patient.user))
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Patient.patient_number.ilike(search_pattern)) |
            (Patient.user.has(first_name=search_pattern)) |
            (Patient.user.has(last_name=search_pattern))
        )
    patients = query.order_by(Patient.created_at.desc()).all()

    result = []
    for p in patients:
        p_dict = {
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
        }
        result.append(p_dict)
    return result
