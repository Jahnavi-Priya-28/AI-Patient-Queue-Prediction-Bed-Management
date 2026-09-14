from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshTokenRequest, TokenResponse, UserResponse, AdminCreateUserRequest
from app.services.auth import register_user, authenticate_user, refresh_token_service, create_user_by_admin
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.enums import UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a public patient account. Staff/admin roles are created through authorized administration."""
    return register_user(db, req)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with email and password. Backend determines role and organization."""
    return authenticate_user(db, req)


@router.post("/admin/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def admin_create_user(
    req: AdminCreateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.HOSPITAL_ADMIN, UserRole.SUPER_ADMIN])),
):
    """Create hospital staff accounts within the caller's authorization scope."""
    return create_user_by_admin(db, req, current_user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh an expired JWT access token using a valid refresh token."""
    return refresh_token_service(db, req.refresh_token)


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Logout current user session."""
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Fetch profile info for the authenticated database account."""
    return current_user
