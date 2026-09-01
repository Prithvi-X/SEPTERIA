from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.voice import VoicePatternDeviationResponse

class MultimodalEvaluateRequest(BaseModel):
    personnel_id: Optional[str] = Field(None, description="Identifier of the personnel member.")
    features: Optional[Dict[str, Optional[float]]] = Field(None, description="60-second window wearable telemetry features.")
    p_physio: Optional[float] = Field(None, ge=0.0, le=1.0, description="Raw or calibrated physiological stress probability.")
    data_quality_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Physiological data quality score [0.0, 1.0].")
    is_physical_exertion: bool = Field(default=False, description="Physical exertion disambiguation flag.")
    z_autonomic: float = Field(default=0.0, description="Personal autonomic strain z-score relative to baseline.")
    recovery_burden_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Phase 5 composite recovery burden score.")
    sleep_deficit_hours: float = Field(default=0.0, ge=0.0, description="Cumulative sleep debt relative to personal baseline.")
    trajectory_direction: str = Field(default="STABLE", description="Autonomic recovery trajectory: IMPROVING, STABLE, or DETERIORATING.")
    operational_zone: str = Field(default="ZONE_2", description="Operational context: ZONE_1, ZONE_2, or ZONE_3.")
    include_graph_evidence: bool = Field(default=True, description="Whether to include Phase 7 Contextual Graph evidence.")
    include_voice_evidence: bool = Field(default=True, description="Whether to include Phase 8 voluntary voice acoustic evidence.")
    voice_audio_base64: Optional[str] = Field(None, description="Optional voluntary voice check-in audio base64 byte stream.")

class ContributingStreamInfo(BaseModel):
    stream: str
    score: Optional[float] = None
    weight: Optional[float] = None
    context: Optional[str] = None
    z_autonomic: Optional[float] = None
    direction: Optional[str] = None
    sleep_deficit_hours: Optional[float] = None
    summary: Optional[str] = None
    quality: Optional[float] = None
    status: Optional[str] = None

class MultimodalAssessmentResponse(BaseModel):
    personnel_id: Optional[str]
    advisory_welfare_state: str
    composite_welfare_score: float
    multimodal_confidence: float
    evidence_agreement_score: float
    is_evidence_conflict: bool
    conflict_details: Optional[str]
    contributing_streams: List[Dict[str, Any]]
    voice_evidence_included: bool
    voice_summary: Optional[str]
    graph_evidence_included: bool
    graph_summary: Optional[str]
    recommended_action: str
    human_review_required: bool
    timestamp: str

class UnitWelfareSummaryResponse(BaseModel):
    unit_id: str
    total_personnel_evaluated: int
    welfare_states_breakdown: Dict[str, int]
    shared_patterns_count: int
    primary_unit_stressors: List[str]
    recommended_command_actions: List[str]
    data_classification: str = "AGGREGATE_COMMAND_SUMMARY_NO_RAW_BIOMETRICS"
