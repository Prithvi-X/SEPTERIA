from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.schemas.auth import UserCreate
from backend.app.core.security import get_password_hash, verify_password

class AuthService:
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = db.query(User).filter(User.email == user_id).first()
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = AuthService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            role=user_in.role.value if hasattr(user_in.role, "value") else str(user_in.role),
            force=user_in.force,
            unit_id=user_in.unit_id,
            is_active=user_in.is_active,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
