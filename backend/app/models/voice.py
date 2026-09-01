import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON, Text, ForeignKey
from backend.app.core.database import Base

class VoiceCheckIn(Base):
    __tablename__ = "voice_checkins"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    personnel_id = Column(String(50), nullable=False, index=True)
    consent_given = Column(Boolean, default=True, nullable=False)
    consent_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration_seconds = Column(Float, default=20.0, nullable=False)
    audio_quality_score = Column(Float, default=1.0, nullable=False)
    speech_quality_score = Column(Float, default=1.0, nullable=False)
    evidence_status = Column(String(50), default="VALID", nullable=False)
    feature_snapshot_json = Column(JSON, nullable=True)
    quality_flags = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class VoiceBaselineRecord(Base):
    __tablename__ = "voice_baselines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    personnel_id = Column(String(50), nullable=False, unique=True, index=True)
    baseline_medians_json = Column(JSON, nullable=True)
    baseline_mads_json = Column(JSON, nullable=True)
    observation_count = Column(Float, default=0, nullable=False)
    baseline_quality_score = Column(Float, default=0.0, nullable=False)
    is_established = Column(Boolean, default=False, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)
