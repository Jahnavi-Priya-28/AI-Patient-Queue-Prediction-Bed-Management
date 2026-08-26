import sys
import os
from datetime import datetime, date, time, timedelta

# Add backend directory to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.db.session import engine
from app.db.base import Base
from app.core.config import settings
from app.core.security import hash_password
from app.models.enums import UserRole, BedStatus, PriorityLevel, AppointmentStatus, QueueStatus
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.department import Department
from app.models.ward import Ward
from app.models.bed import Bed
from app.models.appointment import Appointment
from app.models.queue_entry import QueueEntry


def seed_database():
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    print("[+] Seeding PatientFlow AI Database...")

    # 1. Departments
    dept_data = [
        ("Emergency", "EMERG", "24/7 Emergency Care & Triage"),
        ("Cardiology", "CARD", "Heart & Cardiovascular Care"),
        ("Orthopedics", "ORTHO", "Bone, Joint & Musculoskeletal Care"),
        ("General Medicine", "GENMED", "Primary Healthcare & Diagnostics"),
        ("ENT", "ENT", "Ear, Nose, Throat Specialist Care"),
        ("Pediatrics", "PED", "Infant, Child & Adolescent Care"),
    ]
    departments = {}
    for name, code, desc in dept_data:
        dept = db.query(Department).filter(Department.code == code).first()
        if not dept:
            dept = Department(name=name, code=code, description=desc, active=True)
            db.add(dept)
            db.flush()
        departments[code] = dept

    # 2. Admin User
    admin = db.query(User).filter(User.email == "admin@patientflow.ai").first()
    if not admin:
        admin = User(
            email="admin@patientflow.ai",
            password_hash=hash_password("AdminPassword123!"),
            role=UserRole.ADMIN,
            first_name="Hospital",
            last_name="Administrator",
            phone="+18005550100",
            is_active=True,
        )
        db.add(admin)

    # 3. Receptionist User
    receptionist = db.query(User).filter(User.email == "receptionist@patientflow.ai").first()
    if not receptionist:
        receptionist = User(
            email="receptionist@patientflow.ai",
            password_hash=hash_password("ReceptionistPassword123!"),
            role=UserRole.RECEPTIONIST,
            first_name="Jane",
            last_name="Smith",
            phone="+18005550101",
            is_active=True,
        )
        db.add(receptionist)

    # 4. Doctors
    doctor_specs = [
        ("dr.sarah@patientflow.ai", "Sarah", "Jenkins", "EMERG", "DOC-101", "Emergency Medicine", 15),
        ("dr.robert@patientflow.ai", "Robert", "Chen", "CARD", "DOC-102", "Interventional Cardiology", 20),
        ("dr.emily@patientflow.ai", "Emily", "Davis", "ORTHO", "DOC-103", "Orthopedic Surgery", 20),
        ("dr.michael@patientflow.ai", "Michael", "Taylor", "GENMED", "DOC-104", "Internal Medicine", 15),
        ("dr.amanda@patientflow.ai", "Amanda", "White", "ENT", "DOC-105", "Otolaryngology", 15),
        ("dr.james@patientflow.ai", "James", "Wilson", "PED", "DOC-106", "Pediatric Care", 15),
    ]
    doctors = {}
    for email, fn, ln, dept_code, emp_no, spec, duration in doctor_specs:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                password_hash=hash_password("DoctorPassword123!"),
                role=UserRole.DOCTOR,
                first_name=fn,
                last_name=ln,
                phone=f"+1800555{emp_no.split('-')[1]}",
                is_active=True,
            )
            db.add(user)
            db.flush()

        doc = db.query(Doctor).filter(Doctor.user_id == user.id).first()
        if not doc:
            doc = Doctor(
                user_id=user.id,
                department_id=departments[dept_code].id,
                employee_number=emp_no,
                specialization=spec,
                consultation_duration=duration,
                is_available=True,
            )
            db.add(doc)
            db.flush()
        doctors[dept_code] = doc

    # 5. Wards & Beds
    ward_specs = [
        ("Emergency Ward", "Emergency", 1, 10),
        ("ICU Ward", "ICU", 1, 8),
        ("General Surgical Ward", "Surgical", 2, 15),
        ("Pediatric Ward", "Pediatric", 3, 12),
    ]
    for name, wtype, floor, capacity in ward_specs:
        ward = db.query(Ward).filter(Ward.name == name).first()
        if not ward:
            ward = Ward(name=name, ward_type=wtype, floor=floor, capacity=capacity, active=True)
            db.add(ward)
            db.flush()

            # Seed beds for ward
            for b_num in range(1, capacity + 1):
                status = BedStatus.AVAILABLE
                if b_num in [1, 2]:
                    status = BedStatus.OCCUPIED
                elif b_num == 3:
                    status = BedStatus.CLEANING
                elif b_num == 4:
                    status = BedStatus.MAINTENANCE

                bed = Bed(
                    ward_id=ward.id,
                    bed_number=f"{wtype[:3].upper()}-{floor}0{b_num}",
                    status=status,
                )
                db.add(bed)

    db.commit()
    print("[SUCCESS] Seed Data Inserted Successfully!")


if __name__ == "__main__":
    seed_database()
