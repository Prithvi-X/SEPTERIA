from datetime import datetime
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from backend.app.core.database import Base

class OperationalContext(Base):
    __tablename__ = "operational_contexts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(255), nullable=True) # e.g. "Border Deployment Alpha"
    personnel_id = Column(String(50), nullable=True, index=True) # Optional if assigned per unit
    unit_id = Column(String(50), nullable=True, index=True)
    zone = Column(String(100), nullable=False) # Zone 1 (Active Ops), Zone 2 (Border/Remote), Zone 3 (Critical Incident)
    duty_type = Column(String(100), nullable=False) # e.g. Static Guard, Border Patrol, Night Duty, QRT
    shift = Column(String(100), nullable=False) # e.g. Day, Night, 12-hr
    location = Column(String(255), nullable=False)
    environment = Column(String(100), nullable=False) # High Heat, Extreme Cold, High Altitude, Standard
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    temporary = Column(Boolean, default=False, nullable=False)
    auto_revert = Column(Boolean, default=True, nullable=False)
    status = Column(String(50), default="ACTIVE", nullable=False) # ACTIVE, EXPIRED, REVERTED, CANCELLED
    previous_context_snapshot = Column(JSON, nullable=True) # Stores baseline snapshot for deterministic auto-reversion
    notes = Column(Text, nullable=True)
    source = Column(String(50), default="AUTHORITY", nullable=False) # AUTHORITY / SYSTEM
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
