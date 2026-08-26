from datetime import datetime, timezone
import random
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.patient import Patient
from app.models.enums import UserRole
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.config import settings


def generate_patient_number() -> str:
    today_str = datetime.now().strftime("%Y%m%d")
    rand_suffix = random.randint(1000, 9999)
    return f"PAT-{today_str}-{rand_suffix}"


def register_user(db: Session, req: RegisterRequest) -> User:
    existing_user = db.query(User).filter(User.email == req.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists",
        )
    
    hashed_pw = hash_password(req.password)
    user = User(
        email=req.email.lower(),
        password_hash=hashed_pw,
        role=req.role,
        first_name=req.first_name,
        last_name=req.last_name,
        phone=req.phone,
        is_active=True,
    )
    db.add(user)
    db.flush() # Flush to get user.id

    # If role is PATIENT, create Patient profile
    if req.role == UserRole.PATIENT:
        patient = Patient(
            user_id=user.id,
            patient_number=generate_patient_number(),
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is deactivated",
        )
    
    # Update last login timestamp
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    access_token = create_access_token(subject=user.id, role=user.role.value)
    refresh_token = create_refresh_token(subject=user.id, role=user.role.value)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user,
    }


def refresh_token_service(db: Session, refresh_token: str) -> dict:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type for refresh",
        )
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    new_access_token = create_access_token(subject=user.id, role=user.role.value)
    new_refresh_token = create_refresh_token(subject=user.id, role=user.role.value)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user,
    }
