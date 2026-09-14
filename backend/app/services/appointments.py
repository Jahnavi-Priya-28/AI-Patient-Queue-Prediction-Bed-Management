from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.department import Department
from app.models.enums import AppointmentStatus, UserRole
from app.models.user import User
from app.schemas.domain import AppointmentCreate


def create_appointment(db: Session, current_user: User, req: AppointmentCreate) -> Appointment:
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found for current user")

    doctor = db.query(Doctor).filter(Doctor.id == req.doctor_id, Doctor.organization_id == patient.organization_id).first()
    department = db.query(Department).filter(Department.id == req.department_id, Department.organization_id == patient.organization_id).first()
    if not doctor or not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor or department not found in this hospital")

    appt = Appointment(
        patient_id=patient.id,
        organization_id=patient.organization_id,
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


def get_appointments(db: Session, current_user: User, appt_date: Optional[date] = None) -> List[Appointment]:
    query = db.query(Appointment).options(
        joinedload(Appointment.patient).joinedload(Patient.user),
        joinedload(Appointment.doctor).joinedload(Doctor.user),
        joinedload(Appointment.department),
    )
    if current_user.role != UserRole.SUPER_ADMIN:
        query = query.filter(Appointment.organization_id == current_user.organization_id)
    if current_user.role == UserRole.PATIENT:
        if not current_user.patient_profile:
            return []
        query = query.filter(Appointment.patient_id == current_user.patient_profile.id)
    if current_user.role == UserRole.DOCTOR:
        if not current_user.doctor_profile:
            return []
        query = query.filter(Appointment.doctor_id == current_user.doctor_profile.id)
    if appt_date:
        query = query.filter(Appointment.appointment_date == appt_date)
    return query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.asc()).all()
