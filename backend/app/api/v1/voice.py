from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.voice import (
    VoiceCheckInSubmitRequest,
    VoiceCheckInResponse,
    VoiceBaselineResponse,
)
from backend.app.services.voice_service import VoiceService
from backend.app.engine.voice.voice_feature_extractor import VoiceFeatureExtractor

router = APIRouter(prefix="/voice", tags=["Voice Intelligence & Acoustic Check-In"])

@router.post(
    "/check-in",
    response_model=VoiceCheckInResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit voluntary voice check-in for acoustic analysis",
)
def submit_voluntary_voice_checkin(
    req: VoiceCheckInSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submits an optional, user-initiated 20-30s voice check-in audio sample.
    Extracts acoustic features, calculates personal baseline deviation, and returns non-diagnostic indicators.
    Privacy guarantee: Raw audio bytes are never stored on disk or in database.
    """
    return VoiceService.process_voice_checkin(db=db, user=current_user, req=req)

@router.get(
    "/status",
    response_model=VoiceBaselineResponse,
    summary="Get authenticated personnel personal voice baseline status",
)
def get_personal_voice_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns personal baseline acoustic metadata and readiness state (minimum 3 samples required).
    """
    return VoiceService.get_voice_status(db=db, user=current_user)

@router.get(
    "/history",
    response_model=List[Dict[str, Any]],
    summary="Get personal historical voice feature snapshots",
)
def get_personal_voice_history(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns historical acoustic feature snapshots for the authenticated user.
    """
    return VoiceService.get_voice_history(db=db, user=current_user, limit=limit)

@router.post(
    "/demo-sample",
    summary="Generate synthetic voice sample base64 for testing",
)
def generate_synthetic_voice_sample(
    duration_seconds: float = Query(default=20.0, ge=5.0, le=45.0),
    pitch_f0_hz: float = Query(default=125.0, ge=80.0, le=300.0),
    speech_rate_multiplier: float = Query(default=1.0, ge=0.5, le=2.0),
    current_user: User = Depends(get_current_user),
):
    """
    Generates a controlled synthetic WAV audio base64 stream for testing audio pipeline without hardware mic.
    """
    import base64
    extractor = VoiceFeatureExtractor()
    audio_bytes = extractor.generate_synthetic_audio(
        duration_seconds=duration_seconds,
        pitch_f0_hz=pitch_f0_hz,
        speech_rate_multiplier=speech_rate_multiplier,
    )
    b64_str = base64.b64encode(audio_bytes).decode("utf-8")
    return {
        "audio_base64": b64_str,
        "duration_seconds": duration_seconds,
        "format": "audio/wav",
        "sample_rate": 16000,
        "message": "Synthetic voice audio generated successfully."
    }
