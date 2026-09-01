from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, DateTime, Boolean, JSON
from backend.app.core.database import Base
from shared.constants.evidence import EvidenceStatus, SQIStatus, MotionContext

class PhysiologicalRecord(Base):
    __tablename__ = "physiological_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    personnel_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Core Physiological Metrics
    hr = Column(Float, nullable=False) # Heart Rate (bpm)
    hrv = Column(Float, nullable=False) # Heart Rate Variability (rMSSD in ms)
    resting_hr = Column(Float, nullable=False) # Resting Heart Rate (bpm)
    sleep = Column(Float, nullable=False) # Sleep duration in hours
    activity = Column(Float, nullable=False) # Active minutes / step index
    respiration = Column(Float, nullable=True) # Breaths/min
    temperature = Column(Float, nullable=True) # Skin/Body temp in deg C
    
    # Phase 4 Signal Quality & Provenance Extensions
    signal_quality = Column(Float, default=1.0, nullable=False) # 0.0 - 1.0 numerical confidence
    sqi_status = Column(String(20), default=SQIStatus.GOOD.value, nullable=False) # GOOD, FAIR, POOR, MISSING
    evidence_status = Column(String(50), default=EvidenceStatus.OBSERVED.value, nullable=False) # OBSERVED, DERIVED, INFERRED, UNCERTAIN
    motion_context = Column(String(50), default=MotionContext.LOW.value, nullable=False) # LOW, MODERATE, HIGH, EXERTIONAL
    
    # Provenance Metadata
    source = Column(String(50), default="synthetic_wearable", nullable=False) # synthetic_wearable, api_ingestion, device_ble
    device_type = Column(String(100), default="synthetic_smartband", nullable=True)
    is_synthetic = Column(Boolean, default=True, nullable=False)
    raw_data_snapshot = Column(JSON, nullable=True) # Original pre-normalized payload for auditability
    processing_version = Column(String(20), default="v1.0", nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
