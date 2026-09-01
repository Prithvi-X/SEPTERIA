from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from backend.app.core.database import Base

class Personnel(Base):
    __tablename__ = "personnel"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    personnel_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. "CRPF-88219"
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    force = Column(String(50), nullable=False, index=True) # e.g. "CRPF", "BSF", "ITBP", "CISF"
    unit_id = Column(String(50), nullable=False, index=True) # e.g. "BSF-BN-47"
    role = Column(String(100), nullable=False) # e.g. "Head Constable", "Sub-Inspector"
    rank = Column(String(100), nullable=True)
    posting = Column(String(255), nullable=False) # Current base station
    status = Column(String(50), default="ACTIVE", nullable=False, index=True) # ACTIVE, ON_LEAVE, TRANSITION, DEPLOYED
    
    # Active operational context link
    active_context_id = Column(String(36), ForeignKey("operational_contexts.id"), nullable=True)
    
    # Leave & Post-Leave Transition tracking (Authority-managed, 14-day transition window)
    leave_status = Column(String(50), default="NONE", nullable=False) # NONE, ON_LEAVE, POST_LEAVE_TRANSITION
    leave_end_date = Column(DateTime, nullable=True)
    return_date = Column(DateTime, nullable=True)
    transition_start_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
