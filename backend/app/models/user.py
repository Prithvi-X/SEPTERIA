from datetime import datetime
import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from backend.app.core.database import Base
from shared.constants.roles import UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.PERSONNEL.value, nullable=False)
    force = Column(String(50), nullable=True) # e.g. BSF, CRPF, ITBP
    unit_id = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
