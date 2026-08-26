from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.enums import AppointmentStatus
from app.schemas.domain import AppointmentCreate


def create_appointment(db: Session, patient_user_id: int, req: AppointmentCreate) -> Appointment:
    patient = db.query(Patient).filter(Patient.user_id == patient_user_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found for current user",
        )
    
    appt = Appointment(
        patient_id=patient.id,
        doctor_id=req.doctor_id,
        department_id=req.department_id,
        appointment_date=req.appointment_date,
        appointment_time=req.appointment_time,
        appointment_type=req.appointment_type,
        priority=req.priority,
        status=AppointmentStatus.SCHEDULED,
        reason=req.reason,
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


def get_appointments(
    db: Session,
    patient_user_id: Optional[int] = None,
    doctor_user_id: Optional[int] = None,
    appt_date: Optional[date] = None,
) -> List[Appointment]:
    query = db.query(Appointment).options(
        joinedload(Appointment.patient).joinedload(Patient.user),
        joinedload(Appointment.doctor).joinedload(Doctor.user),
        joinedload(Appointment.department),
    )
    if patient_user_id:
        patient = db.query(Patient).filter(Patient.user_id == patient_user_id).first()
        if patient:
            query = query.filter(Appointment.patient_id == patient.id)
    if doctor_user_id:
        from app.models.doctor import Doctor
        doctor = db.query(Doctor).filter(Doctor.user_id == doctor_user_id).first()
        if doctor:
            query = query.filter(Appointment.doctor_id == doctor.id)
    if appt_date:
        query = query.filter(Appointment.appointment_date == appt_date)

    return query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.asc()).all()
