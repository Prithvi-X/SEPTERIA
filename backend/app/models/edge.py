import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, Text, ForeignKey, UniqueConstraint
from backend.app.core.database import Base

class EdgeTelemetryRecord(Base):
    """
    Edge-ingested raw telemetry record with idempotency, provenance, and synchronization tracking.
    """
    __tablename__ = "edge_telemetry_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    idempotency_key = Column(String(64), unique=True, nullable=False, index=True)
    personnel_id = Column(String(50), nullable=False, index=True)
    device_id = Column(String(100), nullable=False, index=True)
    device_source = Column(String(50), nullable=False) # BLE, HEALTH_CONNECT, SYNTHETIC_DEMO
    device_timestamp = Column(DateTime, nullable=False, index=True)
    ingestion_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    sequence_number = Column(Integer, default=0, nullable=False)
    clock_drift_ms = Column(Float, default=0.0, nullable=False)
    sync_status = Column(String(20), default="SYNCED", nullable=False) # SYNCED, PENDING, FAILED
    source_quality = Column(Float, default=1.0, nullable=False)
    raw_payload = Column(JSON, nullable=True)
    physiological_record_id = Column(String(36), nullable=True) # Link to Phase 4 record
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class EdgeDeviceSyncStatus(Base):
    """
    Tracks edge hardware device connectivity, synchronization latency, and queue health.
    """
    __tablename__ = "edge_device_sync_status"

    device_id = Column(String(100), primary_key=True, index=True)
    personnel_id = Column(String(50), nullable=False, index=True)
    device_source = Column(String(50), default="BLE", nullable=False)
    connection_state = Column(String(20), default="CONNECTED", nullable=False) # CONNECTED, DISCONNECTED, RECONNECTING
    last_sync_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_device_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    pending_records_count = Column(Integer, default=0, nullable=False)
    estimated_clock_drift_ms = Column(Float, default=0.0, nullable=False)
    data_completeness_pct = Column(Float, default=100.0, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
