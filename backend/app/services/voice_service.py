"""
SEPTERIA Voice Check-In and Acoustic Baseline Service (Phase 8)

Privacy First:
- Mandatory explicit user consent check.
- Audio is decoded in-memory for acoustic feature extraction and never stored on disk or DB.
- Personal baseline calculated from >= 3 historical samples.
- Non-diagnostic acoustic deviation indicators.
"""

from datetime import datetime
import base64
import json
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.voice import VoiceCheckIn, VoiceBaselineRecord
from backend.app.schemas.voice import (
    VoiceCheckInSubmitRequest,
    VoiceCheckInResponse,
    VoiceBaselineResponse,
    VoicePatternDeviationResponse,
    VoiceFeatureSnapshotResponse,
)
from backend.app.engine.voice.voice_feature_extractor import (
    VoiceFeatureExtractor,
    VoiceFeatureSnapshot,
)
from backend.app.engine.voice.voice_baseline_engine import (
    VoiceBaselineEngine,
    VoiceBaseline,
    VoicePatternDeviation,
)

# Singletons
_extractor = VoiceFeatureExtractor()
_baseline_engine = VoiceBaselineEngine(min_baseline_samples=3)

class VoiceService:
    @staticmethod
    def process_voice_checkin(
        db: Session,
        user: User,
        req: VoiceCheckInSubmitRequest
    ) -> VoiceCheckInResponse:
        """
        Processes voluntary voice check-in: verifies consent, extracts acoustic features,
        evaluates personal baseline deviation, and persists feature snapshot (zero raw audio retained).
        """
        if not req.consent_given:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Explicit voluntary consent is required before performing a voice check-in."
            )

        personnel_id = str(user.id)

        # 1. Decode Audio Bytes
        if req.audio_base64:
            try:
                audio_bytes = base64.b64decode(req.audio_base64)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid base64 audio encoding: {str(e)}"
                )
        else:
            # Generate synthetic clean speech for development/demo testing
            audio_bytes = _extractor.generate_synthetic_audio(
                duration_seconds=req.duration_seconds,
                pitch_f0_hz=125.0,
                speech_rate_multiplier=1.0,
                energy_level=0.25
            )

        # 2. Extract Acoustic Features
        snapshot: VoiceFeatureSnapshot = _extractor.extract_features(audio_bytes)

        # 3. Retrieve Historical Snapshots for Baseline Computation
        historical_records = (
            db.query(VoiceCheckIn)
            .filter(VoiceCheckIn.personnel_id == personnel_id)
            .order_by(VoiceCheckIn.created_at.desc())
            .limit(20)
            .all()
        )

        history_list = []
        for r in historical_records:
            if r.feature_snapshot_json:
                history_list.append(r.feature_snapshot_json)

        # 4. Compute Personal Baseline
        baseline: VoiceBaseline = _baseline_engine.compute_personal_baseline(
            personnel_id=personnel_id,
            historical_snapshots=history_list
        )

        # 5. Evaluate Acoustic Deviation
        deviation: VoicePatternDeviation = _baseline_engine.evaluate_deviation(
            personnel_id=personnel_id,
            current_features=snapshot.feature_values,
            baseline=baseline,
            audio_quality_score=snapshot.audio_quality_score
        )

        # 6. Persist Feature Snapshot (Privacy: Never Store Raw Audio Bytes)
        snapshot_dict = {
            "timestamp": snapshot.timestamp,
            "feature_values": snapshot.feature_values,
            "audio_quality_score": snapshot.audio_quality_score,
            "speech_quality_score": snapshot.speech_quality_score,
            "signal_duration_seconds": snapshot.signal_duration_seconds,
            "evidence_status": snapshot.evidence_status,
            "processing_version": snapshot.processing_version,
            "quality_flags": snapshot.quality_flags,
        }

        db_checkin = VoiceCheckIn(
            personnel_id=personnel_id,
            consent_given=req.consent_given,
            consent_timestamp=datetime.utcnow(),
            duration_seconds=snapshot.signal_duration_seconds,
            audio_quality_score=snapshot.audio_quality_score,
            speech_quality_score=snapshot.speech_quality_score,
            evidence_status=snapshot.evidence_status,
            feature_snapshot_json=snapshot_dict,
            quality_flags=snapshot.quality_flags,
            notes=req.notes,
        )
        db.add(db_checkin)

        # 7. Update Baseline DB Record
        db_base = db.query(VoiceBaselineRecord).filter(VoiceBaselineRecord.personnel_id == personnel_id).first()
        if not db_base:
            db_base = VoiceBaselineRecord(
                personnel_id=personnel_id,
                baseline_medians_json=baseline.baseline_medians,
                baseline_mads_json=baseline.baseline_mads,
                observation_count=baseline.observation_count + (1 if snapshot.evidence_status == "VALID" else 0),
                baseline_quality_score=baseline.baseline_quality_score,
                is_established=baseline.is_established,
                last_updated=datetime.utcnow(),
            )
            db.add(db_base)
        else:
            db_base.baseline_medians_json = baseline.baseline_medians
            db_base.baseline_mads_json = baseline.baseline_mads
            db_base.observation_count = baseline.observation_count + (1 if snapshot.evidence_status == "VALID" else 0)
            db_base.baseline_quality_score = baseline.baseline_quality_score
            db_base.is_established = baseline.is_established
            db_base.last_updated = datetime.utcnow()

        db.commit()
        db.refresh(db_checkin)

        # 8. Build Response
        dev_resp = VoicePatternDeviationResponse(
            personnel_id=deviation.personnel_id,
            has_valid_baseline=deviation.has_valid_baseline,
            status=deviation.status,
            deviation_magnitude=round(deviation.deviation_magnitude, 3),
            direction=deviation.direction,
            z_scores={k: round(v, 2) for k, v in deviation.z_scores.items()},
            primary_acoustic_shifts=deviation.primary_acoustic_shifts,
            evidence_quality=round(deviation.evidence_quality, 2),
            non_diagnostic_summary=deviation.non_diagnostic_summary,
            timestamp=deviation.timestamp,
        )

        snap_resp = VoiceFeatureSnapshotResponse(
            timestamp=snapshot.timestamp,
            feature_values={k: round(v, 4) for k, v in snapshot.feature_values.items()},
            audio_quality_score=round(snapshot.audio_quality_score, 2),
            speech_quality_score=round(snapshot.speech_quality_score, 2),
            signal_duration_seconds=round(snapshot.signal_duration_seconds, 1),
            evidence_status=snapshot.evidence_status,
            processing_version=snapshot.processing_version,
            quality_flags=snapshot.quality_flags,
        )

        return VoiceCheckInResponse(
            checkin_id=db_checkin.id,
            personnel_id=personnel_id,
            consent_given=True,
            duration_seconds=round(snapshot.signal_duration_seconds, 1),
            audio_quality_score=round(snapshot.audio_quality_score, 2),
            speech_quality_score=round(snapshot.speech_quality_score, 2),
            evidence_status=snapshot.evidence_status,
            raw_audio_retained=False,
            deviation=dev_resp,
            feature_snapshot=snap_resp,
            message="Voluntary voice check-in analyzed successfully. Raw audio discarded; acoustic metrics preserved."
        )

    @staticmethod
    def get_voice_status(db: Session, user: User) -> VoiceBaselineResponse:
        """
        Retrieves personal baseline acoustic metadata for the authenticated user.
        """
        personnel_id = str(user.id)
        db_base = db.query(VoiceBaselineRecord).filter(VoiceBaselineRecord.personnel_id == personnel_id).first()

        if not db_base or not db_base.is_established:
            return VoiceBaselineResponse(
                personnel_id=personnel_id,
                observation_count=int(db_base.observation_count) if db_base else 0,
                baseline_quality_score=float(db_base.baseline_quality_score) if db_base else 0.0,
                is_established=False,
                status="VOICE_BASELINE_UNAVAILABLE",
                baseline_medians={},
                baseline_mads={},
                last_updated=datetime.utcnow().isoformat(),
            )

        return VoiceBaselineResponse(
            personnel_id=personnel_id,
            observation_count=int(db_base.observation_count),
            baseline_quality_score=round(float(db_base.baseline_quality_score), 2),
            is_established=True,
            status="VOICE_BASELINE_ESTABLISHED",
            baseline_medians={k: round(v, 2) for k, v in (db_base.baseline_medians_json or {}).items()},
            baseline_mads={k: round(v, 2) for k, v in (db_base.baseline_mads_json or {}).items()},
            last_updated=db_base.last_updated.isoformat(),
        )

    @staticmethod
    def get_voice_history(db: Session, user: User, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves historical acoustic feature snapshots for the authenticated user.
        """
        personnel_id = str(user.id)
        records = (
            db.query(VoiceCheckIn)
            .filter(VoiceCheckIn.personnel_id == personnel_id)
            .order_by(VoiceCheckIn.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "checkin_id": r.id,
                "created_at": r.created_at.isoformat(),
                "duration_seconds": r.duration_seconds,
                "audio_quality_score": r.audio_quality_score,
                "speech_quality_score": r.speech_quality_score,
                "evidence_status": r.evidence_status,
                "feature_snapshot": r.feature_snapshot_json,
                "notes": r.notes,
            }
            for r in records
        ]
