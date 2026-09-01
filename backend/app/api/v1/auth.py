from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import create_access_token
from backend.app.schemas.auth import LoginRequest, LoginResponse, UserResponse
from backend.app.services.auth_service import AuthService
from backend.app.api.deps import get_current_user, require_roles
from backend.app.models.user import User
from shared.constants.roles import UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user with email and password, issuing a signed JWT access token.
    """
    from backend.app.core.logging import logger
    logger.info(f"Login attempt for email: '{login_data.email}'")
    user = AuthService.authenticate_user(db, login_data.email, login_data.password)
    logger.info(f"User lookup result: {user}")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )
    
    access_token = create_access_token(
        subject=user.id,
        role=user.role,
        extra_claims={
            "email": user.email,
            "force": user.force,
            "unit_id": user.unit_id,
        }
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )

@router.get("/me", response_model=UserResponse)
def get_current_authenticated_user(current_user: User = Depends(get_current_user)):
    """
    Protected endpoint: returns the authenticated user's profile.
    """
    return UserResponse.model_validate(current_user)

@router.get("/verify-commander", response_model=UserResponse)
def verify_commander_access(current_user: User = Depends(require_roles(UserRole.COMMANDER, UserRole.ADMIN))):
    """
    Protected RBAC endpoint: verifies commander/admin access.
    """
    return UserResponse.model_validate(current_user)
