from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, DateTime, JSON
from backend.app.core.database import Base
from shared.constants.evidence import EvidenceStatus, RiskLevel, Trajectory

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    personnel_id = Column(String(50), nullable=False, index=True)
    risk_level = Column(String(50), default=RiskLevel.LOW.value, nullable=False) # LOW, MODERATE, HIGH
    confidence = Column(Float, nullable=False) # 0.0 - 1.0
    trajectory = Column(String(50), default=Trajectory.STABLE.value, nullable=False) # STABLE, IMPROVING, DETERIORATING
    contributing_factors = Column(JSON, default=list, nullable=False) # List of driver factors with weights
    evidence_status = Column(String(50), default=EvidenceStatus.INFERRED.value, nullable=False)
    model_version = Column(String(100), default="xgb-proto-v1.0", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
