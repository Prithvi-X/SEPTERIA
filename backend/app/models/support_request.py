from datetime import datetime
import uuid
from sqlalchemy import Column, String, Text, DateTime
from backend.app.core.database import Base

class SupportRequest(Base):
    __tablename__ = "support_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    personnel_id = Column(String(50), nullable=False, index=True)
    urgency = Column(String(20), default="ROUTINE", nullable=False) # ROUTINE, MODERATE, PRIORITY
    note = Column(Text, nullable=True)
    status = Column(String(20), default="PENDING", nullable=False) # PENDING, REVIEWED, CLOSED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
