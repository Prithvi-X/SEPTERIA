from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class PhysiologicalIngestItem(BaseModel):
    timestamp: Optional[Any] = None
    hr: Optional[float] = Field(default=None, description="Heart rate in bpm")
    hrv: Optional[float] = Field(default=None, description="HRV (rMSSD) in ms")
    resting_hr: Optional[float] = Field(default=None, description="Resting heart rate in bpm")
    sleep: Optional[float] = Field(default=None, description="Sleep duration in hours")
    activity: Optional[float] = Field(default=0.0, description="Activity motion index / steps")
    respiration: Optional[float] = Field(default=None, description="Breaths per minute")
    temperature: Optional[float] = Field(default=None, description="Body/skin temperature in Celsius")
    signal_quality: Optional[float] = Field(default=1.0, description="Sensor reported quality 0.0-1.0")
    source: Optional[str] = Field(default="api_ingestion")
    device_type: Optional[str] = Field(default="smartband_v1")
    is_synthetic: Optional[bool] = Field(default=False)

class PhysiologicalBatchIngestRequest(BaseModel):
    personnel_id: str
    records: List[PhysiologicalIngestItem]
    adapter_source: Optional[str] = Field(default="api_adapter")

class MissingIntervalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    personnel_id: str
    signal_name: str
    start_time: datetime
    end_time: datetime
    duration_minutes: float
    gap_type: str
    reconstructed: bool
    reconstruction_method: Optional[str] = None

class IngestionResultResponse(BaseModel):
    status: str
    personnel_id: str
    total_received: int
    accepted_count: int
    rejected_count: int
    validation_errors: List[str]
    validation_warnings: List[str]
    detected_gaps_count: int
    overall_sqi: str
    timestamp: datetime

class SignalQualitySummaryResponse(BaseModel):
    personnel_id: str
    overall_quality: str
    overall_completeness_pct: float
    completeness_breakdown: Dict[str, float] # Physiological, Wellness, Operational, Environmental
    signals: Dict[str, str] # hr, hrv, sleep, activity
    missing_intervals: List[MissingIntervalRead]
    contextual_warnings: List[str]
    attribution_summary: str
    timestamp: datetime

class DemoScenarioRequest(BaseModel):
    scenario_code: str = Field(..., description="Scenario code: A, B, C, D, E, F, or G")
    personnel_id: Optional[str] = Field(default="P-1047")
    days: Optional[int] = Field(default=7, ge=1, le=30)

class DemoScenarioResponse(BaseModel):
    scenario_code: str
    scenario_name: str
    personnel_id: str
    records_ingested: int
    detected_gaps: int
    overall_sqi: str
    completeness_pct: float
    attribution_summary: str
    motion_context: str
    timestamp: datetime

class EnrichedTrendItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    timestamp: datetime
    hr: Optional[float] = None
    hrv: Optional[float] = None
    resting_hr: Optional[float] = None
    sleep: Optional[float] = None
    activity: float = 0.0
    respiration: Optional[float] = None
    temperature: Optional[float] = None
    signal_quality: float = 1.0
    sqi_status: str = "GOOD"
    evidence_status: str = "OBSERVED"
    motion_context: str = "LOW"
    source: str = "synthetic_wearable"
    device_type: Optional[str] = None
    is_synthetic: bool = True
    is_reconstructed: bool = False

class EnrichedTrendResponse(BaseModel):
    personnel_id: str
    overall_sqi: str
    data_completeness_pct: float
    latest_hr: float
    latest_hrv: float
    latest_resting_hr: float
    latest_sleep: float
    latest_activity: float
    attribution_summary: str
    trends: List[EnrichedTrendItem]
    evidence_status: str = "OBSERVED"
