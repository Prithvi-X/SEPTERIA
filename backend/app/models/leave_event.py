from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from backend.app.core.database import Base

class LeaveEvent(Base):
    __tablename__ = "leave_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    personnel_id = Column(String(50), nullable=False, index=True) # e.g. "CRPF-88219"
    leave_type = Column(String(100), default="ANNUAL_LEAVE", nullable=False) # ANNUAL_LEAVE, CASUAL_LEAVE, MEDICAL_LEAVE
    leave_start_date = Column(DateTime, nullable=True)
    leave_end_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=False)
    transition_days_total = Column(Integer, default=14, nullable=False) # 14-day transition tracking window
    status = Column(String(50), default="ACTIVE_TRANSITION", nullable=False) # ACTIVE_TRANSITION, COMPLETED
    recorded_by = Column(String(100), nullable=False) # Actor email / ID
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
