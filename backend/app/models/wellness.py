from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime
from backend.app.core.database import Base
from shared.constants.evidence import EvidenceStatus

class WellnessRecord(Base):
    __tablename__ = "wellness_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    personnel_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    fatigue = Column(Integer, nullable=False) # 1-5
    stress = Column(Integer, nullable=False) # 1-5
    mood = Column(Integer, nullable=False) # 1-5
    sleep_quality = Column(Integer, nullable=False) # 1-5
    workload = Column(Integer, nullable=True, default=3) # 1-5
    notes = Column(Text, nullable=True)
    evidence_status = Column(String(50), default=EvidenceStatus.OBSERVED.value, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
