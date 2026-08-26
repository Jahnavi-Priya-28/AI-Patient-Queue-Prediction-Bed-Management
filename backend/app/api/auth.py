from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshTokenRequest, TokenResponse, UserResponse
from app.services.auth import register_user, authenticate_user, refresh_token_service
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_211_CREATED if hasattr(status, "HTTP_211_CREATED") else status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account (Defaults to PATIENT role)."""
    return register_user(db, req)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user with email & password, returning JWT access & refresh tokens."""
    return authenticate_user(db, req)


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
    """Fetch profile info of current authenticated user."""
    return current_user
