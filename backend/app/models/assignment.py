from datetime import datetime
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from backend.app.core.database import Base

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    personnel_id = Column(String(50), nullable=True, index=True)
    unit_id = Column(String(50), nullable=True, index=True)
    context_id = Column(String(36), ForeignKey("operational_contexts.id"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    auto_revert = Column(Boolean, default=True, nullable=False)
    status = Column(String(50), default="ACTIVE", nullable=False) # ACTIVE, EXPIRED, CANCELLED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
