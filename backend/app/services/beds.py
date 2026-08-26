from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.bed import Bed
from app.models.ward import Ward
from app.models.patient import Patient
from app.models.enums import BedStatus


def get_all_wards(db: Session) -> List[Ward]:
    return db.query(Ward).filter(Ward.active == True).order_by(Ward.name).all()


def get_all_beds(db: Session, ward_id: Optional[int] = None, bed_status: Optional[BedStatus] = None) -> List[Bed]:
    query = db.query(Bed).options(
        joinedload(Bed.ward),
        joinedload(Bed.current_patient).joinedload(Patient.user),
    )
    if ward_id:
        query = query.filter(Bed.ward_id == ward_id)
    if bed_status:
        query = query.filter(Bed.status == bed_status)
    return query.order_by(Bed.bed_number).all()


def assign_bed(db: Session, bed_id: int, patient_id: int) -> Bed:
    bed = db.query(Bed).filter(Bed.id == bed_id).first()
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")

    if bed.status != BedStatus.AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot assign bed {bed.bed_number}. Current status is '{bed.status.value}'",
        )

    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    bed.status = BedStatus.OCCUPIED
    bed.current_patient_id = patient.id
    bed.assigned_at = datetime.now(timezone.utc)
    bed.released_at = None

    db.commit()
    db.refresh(bed)
    return bed


def release_bed(db: Session, bed_id: int) -> Bed:
    bed = db.query(Bed).filter(Bed.id == bed_id).first()
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")

    if bed.status != BedStatus.OCCUPIED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot release bed {bed.bed_number}. Bed is not occupied",
        )

    bed.status = BedStatus.CLEANING # Automatically transition to CLEANING state
    bed.current_patient_id = None
    bed.released_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(bed)
    return bed


def update_bed_status(db: Session, bed_id: int, new_status: BedStatus) -> Bed:
    bed = db.query(Bed).filter(Bed.id == bed_id).first()
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")

    bed.status = new_status
    if new_status == BedStatus.AVAILABLE:
        bed.current_patient_id = None

    db.commit()
    db.refresh(bed)
    return bed
