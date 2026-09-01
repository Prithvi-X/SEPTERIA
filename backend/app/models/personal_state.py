from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
from backend.app.core.database import Base

class PersonalStateSnapshot(Base):
    __tablename__ = "personal_state_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    personnel_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    operational_zone = Column(String(100), nullable=False) # Zone 1, Zone 2, Zone 3
    duty_type = Column(String(100), nullable=False)
    shift = Column(String(100), nullable=False)
    
    # Baseline, Deviations & Trajectory Evidence
    baseline_snapshot = Column(JSON, nullable=False) # Snapshot of active personal baselines
    deviations = Column(JSON, nullable=False) # {"hrv_dev": -13.0, "hrv_pct": -23.6, "hrv_z": -2.1, ...}
    trajectories = Column(JSON, nullable=False) # {"hrv": "DETERIORATING", "sleep": "DETERIORATING", "persistence_days": 4}
    
    # Recovery Burden / Debt
    recovery_burden_score = Column(Float, nullable=False) # 0.0 - 100.0 (Provisional prototype score)
    recovery_burden_factors = Column(JSON, nullable=False) # Detailed breakdown of contributing factors
    
    rebound_status = Column(String(50), default="NONE", nullable=False) # REBOUND_OBSERVED, PERSISTENT_DEVIATION, NONE
    transition_state = Column(String(50), default="NONE", nullable=False) # POST_LEAVE_TRANSITION, DEPLOYMENT_START, NONE
    
    evidence_quality = Column(String(20), default="GOOD", nullable=False) # GOOD, FAIR, POOR
    attribution_summary = Column(String(500), nullable=False)
    processing_version = Column(String(20), default="v1.0", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class RecoveryDebtSnapshot(Base):
    __tablename__ = "recovery_debt_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    personnel_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    debt_score = Column(Float, nullable=False) # 0.0 - 100.0
    sleep_deficit_hours = Column(Float, default=0.0, nullable=False)
    hrv_suppression_days = Column(Integer, default=0, nullable=False)
    rhr_elevation_bpm = Column(Float, default=0.0, nullable=False)
    consecutive_high_workload_days = Column(Integer, default=0, nullable=False)
    
    contributing_factors = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
