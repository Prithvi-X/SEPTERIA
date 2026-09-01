from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from shared.constants.roles import UserRole
from shared.constants.zones import OperationalZone
from shared.constants.evidence import (
    EvidenceStatus,
    RiskLevel,
    Trajectory,
    RecommendationPriority,
    RecommendationStatus,
)

class PersonnelBase(BaseModel):
    id: str = Field(..., description="Unique Personnel Identifier")
    force: str = Field(..., description="CAPF Force, e.g., CRPF, BSF, ITBP, CISF, SSB")
    unit_id: str = Field(..., description="Assigned Unit ID")
    role: str = Field(..., description="Operational rank or role")
    posting: str = Field(..., description="Current primary posting location")
    status: str = Field(default="ACTIVE", description="Current status: ACTIVE, ON_LEAVE, TRANSITION, DEPLOYED")

class OperationalContextBase(BaseModel):
    zone: str = Field(default=OperationalZone.ZONE_1.value, description="Current operational zone")
    duty_type: str = Field(..., description="Duty type e.g. Static, Patrol, Night Duty, QRT")
    shift: str = Field(..., description="Shift timing or identifier")
    location: str = Field(..., description="Current geographical location/coordinates")
    environment: str = Field(..., description="Environmental conditions: Extreme Cold, High Heat, High Altitude, Standard")
    start_time: datetime = Field(..., description="Start of current context")
    end_time: Optional[datetime] = Field(None, description="Scheduled end of temporary context")
    temporary: bool = Field(default=False, description="True if temporary deployment or assignment")
    auto_revert: bool = Field(default=True, description="Automatically revert to base context upon expiry")

class WellnessRecordBase(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Record timestamp")
    fatigue: int = Field(..., ge=1, le=5, description="Self-reported fatigue score (1-5)")
    stress: int = Field(..., ge=1, le=5, description="Self-reported stress score (1-5)")
    mood: int = Field(..., ge=1, le=5, description="Self-reported mood score (1-5)")
    sleep_quality: int = Field(..., ge=1, le=5, description="Self-reported sleep quality (1-5)")
    notes: Optional[str] = Field(None, description="Optional private notes")
    evidence_status: EvidenceStatus = Field(default=EvidenceStatus.OBSERVED, description="Evidence status")

class PhysiologicalRecordBase(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Record timestamp")
    hr: float = Field(..., description="Heart Rate in bpm")
    hrv: float = Field(..., description="Heart Rate Variability (rMSSD in ms)")
    resting_hr: float = Field(..., description="Resting Heart Rate in bpm")
    sleep: float = Field(..., description="Sleep duration in hours")
    activity: float = Field(..., description="Active duration or step count")
    respiration: Optional[float] = Field(None, description="Respiration rate in breaths/min")
    temperature: Optional[float] = Field(None, description="Skin/Body temperature in deg C")
    signal_quality: float = Field(default=1.0, ge=0.0, le=1.0, description="Signal quality index (0.0 - 1.0)")
    evidence_status: EvidenceStatus = Field(default=EvidenceStatus.OBSERVED, description="Evidence status")

class PredictionBase(BaseModel):
    risk_level: RiskLevel = Field(..., description="Predicted Risk Level: LOW, MODERATE, HIGH")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model prediction confidence score")
    trajectory: Trajectory = Field(..., description="Trajectory: STABLE, IMPROVING, DETERIORATING")
    contributing_factors: List[Dict[str, Any]] = Field(default_factory=list, description="Top SHAP/driver factors")
    evidence_status: EvidenceStatus = Field(default=EvidenceStatus.INFERRED, description="Evidence status")
    model_version: Optional[str] = Field(default="xgb-proto-v1.0", description="Model version")

class RecommendationBase(BaseModel):
    type: str = Field(..., description="Type of recommendation e.g. REST_ADVISORY, WELFARE_CHECK, DUTY_ROTATION")
    priority: RecommendationPriority = Field(default=RecommendationPriority.ROUTINE, description="Priority level")
    explanation: str = Field(..., description="Explanation of why this action was recommended")
    status: RecommendationStatus = Field(default=RecommendationStatus.PENDING, description="Current status")
