from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.domain import BedResponse, WardResponse, AssignBedRequest
from app.services.beds import get_all_wards, get_all_beds, assign_bed, release_bed, update_bed_status
from app.core.security import require_role
from app.models.enums import UserRole, BedStatus
from app.models.user import User

router = APIRouter(prefix="/beds", tags=["Bed Management"])


@router.get("/wards", response_model=List[WardResponse])
def list_wards(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.RECEPTIONIST, UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN, UserRole.DOCTOR])),
):
    """List hospital wards inside the caller's organization."""
    return get_all_wards(db, current_user)


@router.get("", response_model=List[BedResponse])
def list_beds(
    ward_id: Optional[int] = None,
    bed_status: Optional[BedStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.RECEPTIONIST, UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN, UserRole.DOCTOR])),
):
    """List beds filtered by ward or status inside the caller's organization."""
    return get_all_beds(db, current_user, ward_id, bed_status)


@router.post("/{bed_id}/assign", response_model=BedResponse)
def assign_bed_endpoint(
    bed_id: int,
    req: AssignBedRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.RECEPTIONIST, UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN])),
):
    """Assign patient to an AVAILABLE bed in the caller's hospital."""
    return assign_bed(db, current_user, bed_id, req.patient_id)


@router.post("/{bed_id}/release", response_model=BedResponse)
def release_bed_endpoint(
    bed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.RECEPTIONIST, UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN])),
):
    """Release an OCCUPIED bed, automatically transitioning it to CLEANING status."""
    return release_bed(db, current_user, bed_id)


@router.put("/{bed_id}/status", response_model=BedResponse)
def change_bed_status(
    bed_id: int,
    status: BedStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.RECEPTIONIST, UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN])),
):
    """Update bed state (AVAILABLE, OCCUPIED, CLEANING, MAINTENANCE)."""
    return update_bed_status(db, current_user, bed_id, status)
