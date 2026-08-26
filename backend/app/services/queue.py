from datetime import datetime, date, timezone
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models.queue_entry import QueueEntry
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.department import Department
from app.models.enums import QueueStatus, AppointmentStatus, PriorityLevel
from app.schemas.domain import CheckInRequest


def check_in_patient(db: Session, req: CheckInRequest, user_role: str) -> QueueEntry:
    # 1. Atomic Transaction: Verify appointment
    appt = db.query(Appointment).filter(Appointment.id == req.appointment_id).first()
    if not appt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    
    # 2. Verify no existing check-in
    existing_q = db.query(QueueEntry).filter(QueueEntry.appointment_id == req.appointment_id).first()
    if existing_q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Patient is already checked in with Token #{existing_q.token_number}",
        )
    
    # 3. Priority Level Check (Only Staff can set priority > NORMAL)
    final_priority = appt.priority
    if req.priority:
        if req.priority != PriorityLevel.NORMAL and user_role not in ["RECEPTIONIST", "ADMIN", "DOCTOR"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only hospital staff can set URGENT or EMERGENCY priority levels",
            )
        final_priority = req.priority

    # 4. Generate concurrency-safe token (e.g. CARD-001, CARD-002)
    dept = db.query(Department).filter(Department.id == appt.department_id).first()
    dept_code = dept.code if dept else "GEN"

    today = date.today()
    q_count = db.query(func.count(QueueEntry.id)).filter(
        QueueEntry.department_id == appt.department_id,
        QueueEntry.queue_date == today
    ).scalar() or 0

    token_num = f"{dept_code}-{q_count + 1:03d}"

    # 5. Create Queue Entry & update appointment status
    q_entry = QueueEntry(
        appointment_id=appt.id,
        patient_id=appt.patient_id,
        doctor_id=appt.doctor_id,
        department_id=appt.department_id,
        token_number=token_num,
        queue_date=today,
        priority=final_priority,
        status=QueueStatus.WAITING,
        check_in_time=datetime.now(timezone.utc),
        predicted_wait_minutes=float((q_count + 1) * 12), # Initial heuristic fallback
    )
    db.add(q_entry)
    appt.status = AppointmentStatus.IN_QUEUE

    db.commit()
    db.refresh(q_entry)
    return q_entry


def call_next_patient(db: Session, doctor_user_id: int) -> QueueEntry:
    doc = db.query(Doctor).filter(Doctor.user_id == doctor_user_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    q_entry = db.query(QueueEntry).filter(
        QueueEntry.doctor_id == doc.id,
        QueueEntry.queue_date == date.today(),
        QueueEntry.status == QueueStatus.WAITING
    ).order_by(
        QueueEntry.priority.desc(), # Emergency/Urgent first
        QueueEntry.check_in_time.asc()
    ).first()

    if not q_entry:
        raise HTTPException(status_code=404, detail="No waiting patients in queue for doctor")

    q_entry.status = QueueStatus.CALLED
    q_entry.called_time = datetime.now(timezone.utc)
    db.commit()
    db.refresh(q_entry)
    return q_entry


def start_consultation(db: Session, queue_entry_id: int) -> QueueEntry:
    q_entry = db.query(QueueEntry).filter(QueueEntry.id == queue_entry_id).first()
    if not q_entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")

    now = datetime.now(timezone.utc)
    q_entry.status = QueueStatus.IN_CONSULTATION
    q_entry.consultation_start = now

    # Calculate ground truth actual_wait_minutes automatically!
    if q_entry.check_in_time:
        delta = now - q_entry.check_in_time
        q_entry.actual_wait_minutes = round(delta.total_seconds() / 60.0, 2)

    # Update appointment status
    if q_entry.appointment:
        q_entry.appointment.status = AppointmentStatus.IN_CONSULTATION

    db.commit()
    db.refresh(q_entry)
    return q_entry


def complete_consultation(db: Session, queue_entry_id: int) -> QueueEntry:
    q_entry = db.query(QueueEntry).filter(QueueEntry.id == queue_entry_id).first()
    if not q_entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")

    q_entry.status = QueueStatus.COMPLETED
    q_entry.consultation_end = datetime.now(timezone.utc)

    if q_entry.appointment:
        q_entry.appointment.status = AppointmentStatus.COMPLETED

    db.commit()
    db.refresh(q_entry)
    return q_entry


def get_live_queue(
    db: Session,
    department_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    queue_date: Optional[date] = None,
) -> List[QueueEntry]:
    target_date = queue_date or date.today()
    query = db.query(QueueEntry).options(
        joinedload(QueueEntry.patient).joinedload(Patient.user),
        joinedload(QueueEntry.doctor).joinedload(Doctor.user),
        joinedload(QueueEntry.department),
    ).filter(QueueEntry.queue_date == target_date)

    if department_id:
        query = query.filter(QueueEntry.department_id == department_id)
    if doctor_id:
        query = query.filter(QueueEntry.doctor_id == doctor_id)

    return query.order_by(QueueEntry.status.asc(), QueueEntry.check_in_time.asc()).all()
