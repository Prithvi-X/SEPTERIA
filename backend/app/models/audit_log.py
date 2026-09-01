from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, JSON
from backend.app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    actor_id = Column(String(50), nullable=False, index=True)
    actor_role = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False) # e.g. "VIEW_WELFARE_CASE", "BULK_ASSIGN_CONTEXT"
    object_type = Column(String(100), nullable=False) # e.g. "OperationalContext", "WelfareRecord"
    object_id = Column(String(100), nullable=True)
    details = Column(JSON, default=dict, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    outcome = Column(String(50), default="SUCCESS", nullable=False) # SUCCESS, DENIED, ERROR
