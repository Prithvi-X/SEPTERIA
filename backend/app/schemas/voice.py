from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class VoiceCheckInSubmitRequest(BaseModel):
    consent_given: bool = Field(..., description="Explicit user voluntary consent for acoustic feature analysis.")
    audio_base64: Optional[str] = Field(None, description="Base64-encoded audio WAV byte stream (20-30s sample).")
    duration_seconds: float = Field(default=20.0, ge=1.0, le=60.0, description="Duration of recording in seconds.")
    notes: Optional[str] = Field(None, description="Optional user subjective check-in notes.")
    retain_raw_audio: bool = Field(default=False, description="Privacy toggle: Never retain raw audio by default.")

class VoiceFeatureSnapshotResponse(BaseModel):
    timestamp: str
    feature_values: Dict[str, float]
    audio_quality_score: float
    speech_quality_score: float
    signal_duration_seconds: float
    evidence_status: str
    processing_version: str
    quality_flags: List[str]

class VoiceBaselineResponse(BaseModel):
    personnel_id: str
    observation_count: int
    baseline_quality_score: float
    is_established: bool
    status: str
    baseline_medians: Dict[str, float]
    baseline_mads: Dict[str, float]
    last_updated: str

class VoicePatternDeviationResponse(BaseModel):
    personnel_id: str
    has_valid_baseline: bool
    status: str
    deviation_magnitude: float
    direction: str
    z_scores: Dict[str, float]
    primary_acoustic_shifts: List[str]
    evidence_quality: float
    non_diagnostic_summary: str
    timestamp: str

class VoiceCheckInResponse(BaseModel):
    checkin_id: str
    personnel_id: str
    consent_given: bool
    duration_seconds: float
    audio_quality_score: float
    speech_quality_score: float
    evidence_status: str
    raw_audio_retained: bool
    deviation: Optional[VoicePatternDeviationResponse] = None
    feature_snapshot: Optional[VoiceFeatureSnapshotResponse] = None
    message: str
