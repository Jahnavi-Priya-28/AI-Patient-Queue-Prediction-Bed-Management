from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.queue_entry import QueueEntry
from app.models.doctor import Doctor
from app.models.bed import Bed
from app.models.ward import Ward
from app.models.department import Department
from app.models.enums import BedStatus, QueueStatus, UserRole
from app.models.user import User


def _scope(query, model, user: User):
    if user.role != UserRole.SUPER_ADMIN:
        return query.filter(model.organization_id == user.organization_id)
    return query


def get_dashboard_metrics(db: Session, user: User) -> dict:
    today = date.today()

    total_patients = _scope(db.query(func.count(Patient.id)), Patient, user).scalar() or 0
    today_appointments = _scope(db.query(func.count(Appointment.id)), Appointment, user).filter(
        Appointment.appointment_date == today
    ).scalar() or 0
    waiting_patients = _scope(db.query(func.count(QueueEntry.id)), QueueEntry, user).filter(
        QueueEntry.queue_date == today,
        QueueEntry.status == QueueStatus.WAITING,
    ).scalar() or 0
    active_doctors = _scope(db.query(func.count(Doctor.id)), Doctor, user).filter(Doctor.is_available == True).scalar() or 0

    bed_base = db.query(Bed).join(Ward, Bed.ward_id == Ward.id)
    if user.role != UserRole.SUPER_ADMIN:
        bed_base = bed_base.filter(Ward.organization_id == user.organization_id)
    available_beds = bed_base.filter(Bed.status == BedStatus.AVAILABLE).count()
    occupied_beds = bed_base.filter(Bed.status == BedStatus.OCCUPIED).count()

    avg_wait = _scope(db.query(func.avg(QueueEntry.actual_wait_minutes)), QueueEntry, user).filter(
        QueueEntry.queue_date == today,
        QueueEntry.actual_wait_minutes != None,
    ).scalar() or 0
    completed_today = _scope(db.query(func.count(QueueEntry.id)), QueueEntry, user).filter(
        QueueEntry.queue_date == today,
        QueueEntry.status == QueueStatus.COMPLETED,
    ).scalar() or 0

    dept_query = db.query(Department.name, func.count(QueueEntry.id).label("count")).outerjoin(
        QueueEntry,
        (Department.id == QueueEntry.department_id) & (QueueEntry.queue_date == today),
    )
    if user.role != UserRole.SUPER_ADMIN:
        dept_query = dept_query.filter(Department.organization_id == user.organization_id)
    dept_queues = dept_query.group_by(Department.name).all()
    queue_by_dept_list = [{"department": d[0], "waiting_count": d[1]} for d in dept_queues]

    ward_query = db.query(
        Ward.name,
        func.count(Bed.id).label("total"),
        func.sum(case((Bed.status == BedStatus.OCCUPIED, 1), else_=0)).label("occupied"),
    ).join(Bed, Ward.id == Bed.ward_id)
    if user.role != UserRole.SUPER_ADMIN:
        ward_query = ward_query.filter(Ward.organization_id == user.organization_id)
    ward_beds = ward_query.group_by(Ward.name).all()
    bed_occupancy_list = [{"ward": w[0], "total_beds": w[1], "occupied_beds": w[2] or 0} for w in ward_beds]

    return {
        "total_patients": total_patients,
        "today_appointments": today_appointments,
        "waiting_patients": waiting_patients,
        "active_doctors": active_doctors,
        "available_beds": available_beds,
        "occupied_beds": occupied_beds,
        "avg_wait_minutes": round(float(avg_wait), 1),
        "completed_consultations_today": completed_today,
        "queue_by_department": queue_by_dept_list,
        "bed_occupancy_by_ward": bed_occupancy_list,
    }
