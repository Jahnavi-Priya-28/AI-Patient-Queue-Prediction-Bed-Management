from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.doctor import Doctor
from app.models.user import User


def get_all_doctors(db: Session, department_id: Optional[int] = None) -> List[dict]:
    query = db.query(Doctor).options(joinedload(Doctor.department), joinedload(Doctor.user))
    if department_id:
        query = query.filter(Doctor.department_id == department_id)
    doctors = query.all()

    result = []
    for doc in doctors:
        d_dict = {
            "id": doc.id,
            "user_id": doc.user_id,
            "department_id": doc.department_id,
            "employee_number": doc.employee_number,
            "specialization": doc.specialization,
            "consultation_duration": doc.consultation_duration,
            "is_available": doc.is_available,
            "department": doc.department,
            "first_name": doc.user.first_name if doc.user else "",
            "last_name": doc.user.last_name if doc.user else "",
        }
        result.append(d_dict)
    return result
