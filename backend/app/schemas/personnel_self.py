from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class AuthoritativeContextRead(BaseModel):
    zone: str = "Zone 2"
    duty_type: str = "Standard Duty"
    shift: str = "Day (08:00 - 16:00)"
    location: str = "Base Station"
    environment: str = "Standard Base Environment"
    temporary: bool = False
    remaining_duration_formatted: Optional[str] = None
    remaining_seconds: Optional[int] = None
    end_time: Optional[datetime] = None

class PersonnelMeResponse(BaseModel):
    id: str
    personnel_id: str
    force: str
    unit_id: str
    role: str
    rank: Optional[str] = None
    posting: str
    status: str
    authoritative_context: AuthoritativeContextRead
    leave_status: str = "NONE"
    post_leave_day_count: Optional[int] = None
    post_leave_total_days: int = 14
    return_date: Optional[datetime] = None
    data_classification: str = "PERSONNEL_PRIVATE"

class WellnessCheckInRequest(BaseModel):
    stress: int = Field(..., ge=1, le=5, description="Self-reported stress level (1=Very Low, 5=Very High)")
    fatigue: int = Field(..., ge=1, le=5, description="Self-reported fatigue level (1=Fresh, 5=Exhausted)")
    sleep_quality: int = Field(..., ge=1, le=5, description="Self-reported sleep quality (1=Poor, 5=Excellent)")
    mood: int = Field(..., ge=1, le=5, description="Self-reported mood/feeling (1=Distressed, 5=Great)")
    workload: int = Field(default=3, ge=1, le=5, description="Self-reported workload manageability (1=Unmanageable, 5=Highly Manageable)")
    notes: Optional[str] = Field(default=None, max_length=500, description="Optional personal note")

class WellnessRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    personnel_id: str
    timestamp: datetime
    stress: int
    fatigue: int
    sleep_quality: int
    mood: int
    workload: Optional[int] = 3
    notes: Optional[str] = None
    evidence_status: str = "OBSERVED"

class PhysiologicalTrendItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    timestamp: datetime
    hr: float
    hrv: float
    resting_hr: float
    sleep: float
    activity: float
    signal_quality: float = 1.0
    sqi_status: str = "GOOD"
    evidence_status: str = "OBSERVED"
    motion_context: str = "LOW"
    source: str = "synthetic_wearable"
    is_synthetic: bool = True
    is_reconstructed: bool = False

class PhysiologicalTrendResponse(BaseModel):
    personnel_id: str
    latest_hr: float
    latest_hrv: float
    latest_resting_hr: float
    latest_sleep: float
    latest_activity: float
    overall_sqi: str = "GOOD"
    data_completeness_pct: float = 94.0
    attribution_summary: str = "Physiological telemetry within expected baseline resting range."
    trends: List[PhysiologicalTrendItem]
    evidence_status: str = "OBSERVED"

class SupportRequestCreate(BaseModel):
    urgency: str = Field(default="ROUTINE", description="Urgency level: ROUTINE, MODERATE, PRIORITY")
    note: Optional[str] = Field(default=None, max_length=1000, description="Confidential welfare request details")

class SupportRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    personnel_id: str
    urgency: str
    note: Optional[str] = None
    status: str = "PENDING"
    created_at: datetime

class VoiceCheckInRequest(BaseModel):
    consent_given: bool = Field(..., description="Explicit user consent for voluntary voice check-in")
    duration_seconds: Optional[int] = Field(default=20, ge=5, le=60, description="Duration of recorded voice sample")
    notes: Optional[str] = None

class VoiceCheckInResponse(BaseModel):
    status: str
    message: str
    consent_verified: bool
    timestamp: datetime
