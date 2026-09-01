from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class EdgeTelemetryPacket(BaseModel):
    idempotency_key: Optional[str] = Field(None, description="Deterministic unique record hash for deduplication.")
    device_id: str = Field(..., description="Unique hardware identifier or MAC address.")
    device_source: str = Field(..., description="Source type: BLE, HEALTH_CONNECT, or SYNTHETIC_DEMO.")
    device_timestamp: str = Field(..., description="Timestamp recorded by the edge device clock.")
    sequence_number: int = Field(default=0, ge=0, description="Monotonically increasing packet sequence order.")
    hr: float = Field(..., ge=0.0, le=250.0, description="Heart rate in beats per minute.")
    hrv: float = Field(..., ge=0.0, le=350.0, description="Heart rate variability (rMSSD in ms).")
    resting_hr: float = Field(default=65.0, ge=30.0, le=150.0, description="Resting heart rate in bpm.")
    sleep: float = Field(default=7.0, ge=0.0, le=24.0, description="Sleep duration in hours.")
    activity: float = Field(default=0.0, ge=0.0, description="Activity index or step energy.")
    temperature: Optional[float] = Field(None, description="Skin/body temperature in Celsius.")
    respiration: Optional[float] = Field(None, description="Respiration rate in breaths/min.")
    motion_context: Optional[str] = Field(default="LOW", description="Motion classification: LOW, MODERATE, HIGH, EXERTIONAL.")
    source_quality: float = Field(default=1.0, ge=0.0, le=1.0, description="Sensor signal quality index [0.0, 1.0].")
    evidence_status: Optional[str] = Field(default="OBSERVED", description="OBSERVED, DERIVED, INFERRED, UNCERTAIN.")
    raw_payload: Optional[Dict[str, Any]] = Field(None, description="Original unparsed sensor snapshot.")

class EdgeBatchIngestRequest(BaseModel):
    personnel_id: str = Field(..., description="Uniformed personnel identifier.")
    device_id: str = Field(..., description="Device identifier or MAC address.")
    device_source: str = Field(..., description="BLE, HEALTH_CONNECT, or SYNTHETIC_DEMO.")
    packets: List[EdgeTelemetryPacket] = Field(..., description="Batch of edge telemetry records.")

class EdgeBatchIngestResponse(BaseModel):
    status: str
    accepted_count: int
    deduplicated_count: int
    rejected_count: int
    clock_drift_ms: float
    sync_status: str # SYNCED, PENDING, FAILED
    processed_record_ids: List[str]
    provenance: Dict[str, Any]
    message: str

class EdgeDeviceStatusResponse(BaseModel):
    device_id: str
    personnel_id: str
    device_source: str
    connection_state: str
    last_sync_timestamp: str
    pending_records_count: int
    estimated_clock_drift_ms: float
    data_completeness_pct: float

class EdgeAuthoritySummaryResponse(BaseModel):
    total_devices_registered: int
    connected_devices_count: int
    disconnected_devices_count: int
    average_sync_latency_minutes: float
    overall_telemetry_completeness_pct: float
    data_classification: str = "AGGREGATE_COMMAND_SUMMARY_NO_RAW_BIOMETRICS"

class EdgeDemoStreamRequest(BaseModel):
    personnel_id: str = Field(default="BSF-47-01")
    scenario: str = Field(
        default="NORMAL_RECOVERY",
        description="Demo scenario: NORMAL_RECOVERY, PHYSICAL_EXERTION, POOR_SLEEP_RECOVERY_DECLINE, SENSOR_DROPOUT, CONNECTIVITY_LOSS_SYNC"
    )
    num_records: int = Field(default=10, ge=1, le=100)
    simulate_network_disconnect: bool = Field(default=False)
