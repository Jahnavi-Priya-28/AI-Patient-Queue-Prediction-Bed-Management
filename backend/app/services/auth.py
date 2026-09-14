from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.organization import Organization
from app.models.user import User
from app.models.patient import Patient
from app.models.enums import UserRole
from app.schemas.auth import RegisterRequest, LoginRequest, AdminCreateUserRequest
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.config import settings


def get_default_organization(db: Session) -> Organization:
    org = db.query(Organization).filter(Organization.slug == "patientflow-general").first()
    if not org:
        org = Organization(name="PatientFlow General Hospital", slug="patientflow-general", is_active=True)
        db.add(org)
        db.flush()
    return org


def _token_payload(user: User) -> dict:
    return {
        "access_token": create_access_token(subject=user.id, role=user.role.value, organization_id=user.organization_id),
        "refresh_token": create_refresh_token(subject=user.id, role=user.role.value, organization_id=user.organization_id),
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user,
    }


def register_user(db: Session, req: RegisterRequest) -> User:
    existing_user = db.query(User).filter(User.email == req.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists",
        )

    org = get_default_organization(db)
    user = User(
        organization_id=org.id,
        email=req.email.lower(),
        password_hash=hash_password(req.password),
        role=UserRole.PATIENT,
        first_name=req.first_name,
        last_name=req.last_name,
        phone=req.phone,
        is_active=True,
    )
    db.add(user)
    db.flush()

    patient = Patient(
        user_id=user.id,
        organization_id=org.id,
        patient_number=f"PAT-{user.id:06d}",
        phone=req.phone,
    )
    db.add(patient)

    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, req: LoginRequest) -> dict:
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive or suspended",
        )
    if user.organization_id is not None and user.organization and not user.organization.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization is inactive",
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    return _token_payload(user)


def create_user_by_admin(db: Session, req: AdminCreateUserRequest, current_user: User) -> User:
    allowed_by_hospital_admin = {UserRole.DOCTOR, UserRole.RECEPTIONIST, UserRole.PATIENT}
    allowed_by_super_admin = allowed_by_hospital_admin | {UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN}

    if current_user.role == UserRole.HOSPITAL_ADMIN:
        if req.role not in allowed_by_hospital_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hospital admins cannot create platform admins")
        organization_id = current_user.organization_id
    elif current_user.role == UserRole.SUPER_ADMIN:
        if req.role not in allowed_by_super_admin:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported role")
        organization_id = req.organization_id
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    if req.role != UserRole.SUPER_ADMIN and not organization_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization is required for hospital users")

    existing_email = db.query(User).filter(User.email == req.email.lower()).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A user with this email address already exists")

    if organization_id:
        org = db.query(Organization).filter(Organization.id == organization_id, Organization.is_active == True).first()
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    user = User(
        organization_id=organization_id,
        email=req.email.lower(),
        password_hash=hash_password(req.password),
        role=req.role,
        first_name=req.first_name,
        last_name=req.last_name,
        phone=req.phone,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def refresh_token_service(db: Session, refresh_token: str) -> dict:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type for refresh")
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return _token_payload(user)
