from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON
from backend.app.core.database import Base

class Baseline(Base):
    __tablename__ = "baselines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    personnel_id = Column(String(50), nullable=False, index=True)
    metric = Column(String(100), nullable=False, index=True) # "hr", "hrv_rmssd", "resting_hr", "sleep_hours", "activity"
    
    # Robust Statistics
    median = Column(Float, nullable=False)
    mad = Column(Float, nullable=False) # Median Absolute Deviation
    p10 = Column(Float, nullable=True)
    p90 = Column(Float, nullable=True)
    mean = Column(Float, nullable=True)
    std = Column(Float, nullable=True)
    
    # Quality & Provenance
    observation_count = Column(Integer, default=0, nullable=False)
    coverage_pct = Column(Float, default=100.0, nullable=False)
    quality_rating = Column(String(20), default="GOOD", nullable=False) # GOOD, FAIR, LOW
    is_cohort_prior = Column(Boolean, default=False, nullable=False) # True if cold-start prior
    
    baseline_statistics = Column(JSON, nullable=False) # Complete snapshot of statistical parameters
    context_modifiers = Column(JSON, nullable=True) # Context-conditioned adjustment factors
    
    confidence = Column(Float, default=1.0, nullable=False)
    update_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
