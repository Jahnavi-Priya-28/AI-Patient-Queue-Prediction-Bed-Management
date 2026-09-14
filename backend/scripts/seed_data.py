import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.db.session import engine
from app.db.base import Base
from app.core.security import hash_password
from app.models.enums import UserRole, BedStatus
from app.models.organization import Organization
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.department import Department
from app.models.ward import Ward
from app.models.bed import Bed


def upsert_user(db, *, email, password, role, first_name, last_name, organization_id=None, phone=None):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            organization_id=organization_id,
            email=email,
            password_hash=hash_password(password),
            role=role,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            is_active=True,
        )
        db.add(user)
        db.flush()
    else:
        user.organization_id = organization_id
        user.role = role
    return user


def seed_database():
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    print("[+] Seeding PatientFlow AI Database...")

    org = db.query(Organization).filter(Organization.slug == "patientflow-general").first()
    if not org:
        org = Organization(name="PatientFlow General Hospital", slug="patientflow-general", is_active=True)
        db.add(org)
        db.flush()

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
        dept = db.query(Department).filter(Department.organization_id == org.id, Department.code == code).first()
        if not dept:
            dept = Department(organization_id=org.id, name=name, code=code, description=desc, active=True)
            db.add(dept)
            db.flush()
        departments[code] = dept

    upsert_user(db, email="admin@example.com", password="AdminPassword123!", role=UserRole.HOSPITAL_ADMIN, first_name="Hospital", last_name="Administrator", organization_id=org.id, phone="+18005550100")
    upsert_user(db, email="reception@example.com", password="ReceptionPassword123!", role=UserRole.RECEPTIONIST, first_name="Jane", last_name="Smith", organization_id=org.id, phone="+18005550101")
    patient_user = upsert_user(db, email="patient@example.com", password="PatientPassword123!", role=UserRole.PATIENT, first_name="Demo", last_name="Patient", organization_id=org.id, phone="+18005550200")
    if not db.query(Patient).filter(Patient.user_id == patient_user.id).first():
        db.add(Patient(user_id=patient_user.id, organization_id=org.id, patient_number=f"PAT-{patient_user.id:06d}", phone=patient_user.phone))

    doctor_specs = [
        ("doctor@example.com", "Sarah", "Jenkins", "EMERG", "EMP-0101", "Emergency Medicine", 15),
        ("dr.robert@patientflow.ai", "Robert", "Chen", "CARD", "EMP-0102", "Interventional Cardiology", 20),
        ("dr.emily@patientflow.ai", "Emily", "Davis", "ORTHO", "EMP-0103", "Orthopedic Surgery", 20),
        ("dr.michael@patientflow.ai", "Michael", "Taylor", "GENMED", "EMP-0104", "Internal Medicine", 15),
    ]
    for email, fn, ln, dept_code, emp_no, spec, duration in doctor_specs:
        user = upsert_user(db, email=email, password="DoctorPassword123!", role=UserRole.DOCTOR, first_name=fn, last_name=ln, organization_id=org.id, phone=f"+1800555{emp_no.split('-')[1]}")
        doc = db.query(Doctor).filter(Doctor.user_id == user.id).first()
        if not doc:
            doc = Doctor(user_id=user.id, organization_id=org.id, department_id=departments[dept_code].id, employee_number=emp_no, specialization=spec, consultation_duration=duration, is_available=True)
            db.add(doc)
        else:
            doc.organization_id = org.id
            doc.department_id = departments[dept_code].id

    ward_specs = [
        ("Emergency Ward", "Emergency", 1, 10),
        ("ICU Ward", "ICU", 1, 8),
        ("General Surgical Ward", "Surgical", 2, 15),
        ("Pediatric Ward", "Pediatric", 3, 12),
    ]
    for name, wtype, floor, capacity in ward_specs:
        ward = db.query(Ward).filter(Ward.organization_id == org.id, Ward.name == name).first()
        if not ward:
            ward = Ward(organization_id=org.id, name=name, ward_type=wtype, floor=floor, capacity=capacity, active=True)
            db.add(ward)
            db.flush()
            for b_num in range(1, capacity + 1):
                status = BedStatus.AVAILABLE
                if b_num in [1, 2]:
                    status = BedStatus.OCCUPIED
                elif b_num == 3:
                    status = BedStatus.CLEANING
                elif b_num == 4:
                    status = BedStatus.MAINTENANCE
                db.add(Bed(ward_id=ward.id, bed_number=f"{wtype[:3].upper()}-{floor}0{b_num}", status=status))
        else:
            ward.organization_id = org.id

    db.commit()
    db.close()
    print("[SUCCESS] Seed Data Inserted Successfully!")


if __name__ == "__main__":
    seed_database()
