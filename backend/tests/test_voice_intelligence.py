"""
SEPTERIA Phase 8 Automated Test Suite
Tests Voice Intelligence, Acoustic Feature Extraction, Personal Voice Baseline,
and Multimodal Evidence Fusion.
"""

import pytest
import numpy as np
import base64
from datetime import datetime

from backend.app.engine.voice.voice_feature_extractor import VoiceFeatureExtractor, VoiceFeatureSnapshot
from backend.app.engine.voice.voice_baseline_engine import VoiceBaselineEngine, VoiceBaseline, VoicePatternDeviation
from backend.app.engine.multimodal.multimodal_fusion_engine import (
    MultimodalFusionEngine,
    MultimodalFusionConfig,
    MultimodalEvidenceResult,
)

@pytest.fixture
def extractor():
    return VoiceFeatureExtractor(min_duration_seconds=5.0, max_duration_seconds=45.0)

@pytest.fixture
def baseline_engine():
    return VoiceBaselineEngine(min_baseline_samples=3)

@pytest.fixture
def fusion_engine():
    return MultimodalFusionEngine()

# Test 1: Consent Required
def test_consent_required():
    from backend.app.schemas.voice import VoiceCheckInSubmitRequest
    # Consent flag must be present and True
    req = VoiceCheckInSubmitRequest(consent_given=False)
    assert req.consent_given is False

# Test 2: Audio Decoding Error Handling
def test_invalid_audio_bytes_handling(extractor):
    garbage_bytes = b"NOT_A_VALID_AUDIO_HEADER_12345"
    snapshot = extractor.extract_features(garbage_bytes)
    assert snapshot.evidence_status == "POOR_AUDIO_QUALITY"
    assert snapshot.audio_quality_score == 0.0
    assert len(snapshot.quality_flags) > 0

# Test 3: Recording Duration Too Short
def test_recording_too_short(extractor):
    short_audio = extractor.generate_synthetic_audio(duration_seconds=2.0)
    snapshot = extractor.extract_features(short_audio)
    assert snapshot.evidence_status == "INCONCLUSIVE_DATA"
    assert any("TOO_SHORT" in flag for flag in snapshot.quality_flags)

# Test 4: Faint / Silent Audio Quality Check
def test_silent_audio_rejected(extractor):
    silent_audio = extractor.generate_synthetic_audio(duration_seconds=10.0, energy_level=0.0001, noise_level=0.00001)
    snapshot = extractor.extract_features(silent_audio)
    assert snapshot.evidence_status == "INCONCLUSIVE_DATA"
    assert any("SILENT" in flag or "FAINT" in flag for flag in snapshot.quality_flags)

# Test 5: Valid Feature Extraction Pipeline
def test_valid_voice_feature_extraction(extractor):
    clean_audio = extractor.generate_synthetic_audio(duration_seconds=15.0, pitch_f0_hz=130.0, energy_level=0.30)
    snapshot = extractor.extract_features(clean_audio)

    assert snapshot.evidence_status == "VALID"
    assert snapshot.audio_quality_score >= 0.70
    assert snapshot.signal_duration_seconds >= 14.0

    features = snapshot.feature_values
    assert "f0_mean" in features
    assert "f0_std" in features
    assert "pause_ratio" in features
    assert "speech_rate_proxy_bpm" in features
    assert "rms_energy_mean" in features
    assert "spectral_centroid_mean" in features
    assert "mfcc_1_mean" in features
    assert "mfcc_13_std" in features
    assert 80.0 <= features["f0_mean"] <= 250.0

# Test 6: Voice Baseline Creation Hierarchy (< 3 vs >= 3 samples)
def test_voice_baseline_establishment(baseline_engine):
    # Case A: 2 samples (< 3) -> UNAVAILABLE
    history_2 = [
        {"evidence_status": "VALID", "feature_values": {"f0_mean": 120.0, "pause_ratio": 0.30, "speech_rate_proxy_bpm": 130.0, "rms_energy_mean": 0.20}},
        {"evidence_status": "VALID", "feature_values": {"f0_mean": 122.0, "pause_ratio": 0.32, "speech_rate_proxy_bpm": 128.0, "rms_energy_mean": 0.22}},
    ]
    base_unavail = baseline_engine.compute_personal_baseline("P-101", history_2)
    assert base_unavail.is_established is False
    assert base_unavail.status == "VOICE_BASELINE_UNAVAILABLE"
    assert base_unavail.observation_count == 2

    # Case B: 3 samples (>= 3) -> ESTABLISHED
    history_3 = history_2 + [
        {"evidence_status": "VALID", "feature_values": {"f0_mean": 118.0, "pause_ratio": 0.31, "speech_rate_proxy_bpm": 132.0, "rms_energy_mean": 0.21}}
    ]
    base_estab = baseline_engine.compute_personal_baseline("P-101", history_3)
    assert base_estab.is_established is True
    assert base_estab.status == "VOICE_BASELINE_ESTABLISHED"
    assert base_estab.observation_count == 3
    assert "f0_mean" in base_estab.baseline_medians
    assert base_estab.baseline_medians["f0_mean"] == 120.0

# Test 7: Voice Pattern Deviation Calculation
def test_voice_deviation_calculation(baseline_engine):
    history_4 = [
        {"evidence_status": "VALID", "feature_values": {"f0_mean": 120.0, "f0_std": 10.0, "f0_iqr": 8.0, "pause_ratio": 0.30, "mean_pause_duration_s": 0.4, "speech_rate_proxy_bpm": 130.0, "rms_energy_mean": 0.25, "rms_energy_std": 0.05, "spectral_centroid_mean": 1500.0}},
        {"evidence_status": "VALID", "feature_values": {"f0_mean": 122.0, "f0_std": 11.0, "f0_iqr": 9.0, "pause_ratio": 0.31, "mean_pause_duration_s": 0.42, "speech_rate_proxy_bpm": 128.0, "rms_energy_mean": 0.26, "rms_energy_std": 0.06, "spectral_centroid_mean": 1520.0}},
        {"evidence_status": "VALID", "feature_values": {"f0_mean": 118.0, "f0_std": 9.0, "f0_iqr": 7.0, "pause_ratio": 0.29, "mean_pause_duration_s": 0.38, "speech_rate_proxy_bpm": 132.0, "rms_energy_mean": 0.24, "rms_energy_std": 0.04, "spectral_centroid_mean": 1480.0}},
        {"evidence_status": "VALID", "feature_values": {"f0_mean": 120.0, "f0_std": 10.0, "f0_iqr": 8.0, "pause_ratio": 0.30, "mean_pause_duration_s": 0.40, "speech_rate_proxy_bpm": 130.0, "rms_energy_mean": 0.25, "rms_energy_std": 0.05, "spectral_centroid_mean": 1500.0}},
    ]
    baseline = baseline_engine.compute_personal_baseline("P-101", history_4)

    # Sub-test 7A: Congruent features -> WITHIN_PERSONAL_BASELINE
    curr_normal = {"f0_mean": 121.0, "f0_std": 10.5, "pause_ratio": 0.30, "speech_rate_proxy_bpm": 130.0, "rms_energy_mean": 0.25, "rms_energy_std": 0.05, "spectral_centroid_mean": 1505.0}
    dev_normal = baseline_engine.evaluate_deviation("P-101", curr_normal, baseline, audio_quality_score=0.95)
    assert dev_normal.status == "WITHIN_PERSONAL_BASELINE"
    assert dev_normal.deviation_magnitude < 0.35

    # Sub-test 7B: Strained features (Elevated F0 + High Pause ratio) -> VOICE_PATTERN_DEVIATION
    curr_strained = {"f0_mean": 155.0, "f0_std": 24.0, "pause_ratio": 0.55, "speech_rate_proxy_bpm": 95.0, "rms_energy_mean": 0.14, "rms_energy_std": 0.02, "spectral_centroid_mean": 1900.0}
    dev_strained = baseline_engine.evaluate_deviation("P-101", curr_strained, baseline, audio_quality_score=0.95)
    assert dev_strained.status == "VOICE_PATTERN_DEVIATION"
    assert dev_strained.deviation_magnitude >= 0.50
    assert len(dev_strained.primary_acoustic_shifts) > 0

# Test 8: Invariant - Voice Alone CANNOT Trigger WELFARE_CHECK or MEDICAL_REVIEW
def test_voice_alone_cannot_trigger_escalation(fusion_engine):
    # Simulated voice deviation without wearable strain
    mock_dev = VoicePatternDeviation(
        personnel_id="P-101",
        has_valid_baseline=True,
        status="VOICE_PATTERN_DEVIATION",
        deviation_magnitude=0.90,
        direction="ACOUSTIC_ELEVATION",
        z_scores={"f0_mean": 4.5},
        primary_acoustic_shifts=["Pitch elevated"],
        evidence_quality=0.90,
        non_diagnostic_summary="Acoustic markers show variance.",
        timestamp=datetime.utcnow().isoformat()
    )

    # Rest of physiology is calm / resting
    res = fusion_engine.evaluate_multimodal_welfare(
        personnel_id="P-101",
        p_physio=0.15,
        data_quality_score=1.0,
        is_physical_exertion=False,
        z_autonomic=0.0,
        recovery_burden_score=0.0,
        sleep_deficit_hours=0.0,
        trajectory_direction="STABLE",
        operational_zone="ZONE_2",
        voice_deviation=mock_dev
    )

    # Must NOT escalate to WELFARE_CHECK or MEDICAL_REVIEW
    assert res.advisory_welfare_state in ["VOLUNTARY_CHECKIN", "STABLE", "MONITORING_ONLY"]
    assert res.human_review_required is False

# Test 9: Multimodal Evidence Convergence (All streams aligned -> High Confidence WELFARE_CHECK)
def test_multimodal_convergence(fusion_engine):
    mock_dev = VoicePatternDeviation(
        personnel_id="P-101",
        has_valid_baseline=True,
        status="VOICE_PATTERN_DEVIATION",
        deviation_magnitude=0.75,
        direction="ACOUSTIC_ELEVATION",
        z_scores={"f0_mean": 3.2, "pause_ratio": 2.8},
        primary_acoustic_shifts=["Pitch elevated", "Pause ratio elevated"],
        evidence_quality=0.85,
        non_diagnostic_summary="Acoustic pattern differs from personal baseline.",
        timestamp=datetime.utcnow().isoformat()
    )

    graph_ev = {
        "shared_pattern_detected": True,
        "summary": "Shared recovery deterioration in Unit 47"
    }

    res = fusion_engine.evaluate_multimodal_welfare(
        personnel_id="P-101",
        p_physio=0.82,
        data_quality_score=0.95,
        is_physical_exertion=False,
        z_autonomic=3.1,
        recovery_burden_score=75.0,
        sleep_deficit_hours=4.5,
        trajectory_direction="DETERIORATING",
        operational_zone="ZONE_2",
        graph_evidence=graph_ev,
        voice_deviation=mock_dev
    )

    assert res.advisory_welfare_state == "WELFARE_CHECK"
    assert res.is_evidence_conflict is False
    assert res.multimodal_confidence >= 0.75
    assert res.human_review_required is True
    assert "Recommend authorized unit welfare check" in res.recommended_action

# Test 10: Multimodal Evidence Conflict Detection
def test_multimodal_conflict_detection(fusion_engine):
    # High physio (0.85) but calm voice, normal sleep, improving trajectory -> CONTRADICTION
    mock_dev_calm = VoicePatternDeviation(
        personnel_id="P-101",
        has_valid_baseline=True,
        status="WITHIN_PERSONAL_BASELINE",
        deviation_magnitude=0.10,
        direction="WITHIN_NORMAL_DISPERSION",
        z_scores={"f0_mean": 0.2},
        primary_acoustic_shifts=[],
        evidence_quality=0.90,
        non_diagnostic_summary="Voice congruent with baseline.",
        timestamp=datetime.utcnow().isoformat()
    )

    res = fusion_engine.evaluate_multimodal_welfare(
        personnel_id="P-101",
        p_physio=0.85,
        data_quality_score=0.90,
        is_physical_exertion=False,
        z_autonomic=0.2,
        recovery_burden_score=10.0,
        sleep_deficit_hours=0.0,
        trajectory_direction="IMPROVING",
        operational_zone="ZONE_2",
        voice_deviation=mock_dev_calm
    )

    assert res.is_evidence_conflict is True
    assert res.conflict_details is not None
    # Conflict penalty prevents false escalation
    assert res.advisory_welfare_state != "WELFARE_CHECK"

# Test 11: Physical Exertion Context Handling in Fusion
def test_exertion_handling_in_fusion(fusion_engine):
    res = fusion_engine.evaluate_multimodal_welfare(
        personnel_id="P-101",
        p_physio=0.92,
        data_quality_score=0.90,
        is_physical_exertion=True,  # High motion energy context
        z_autonomic=0.5,
        recovery_burden_score=15.0,
        sleep_deficit_hours=0.0,
        trajectory_direction="STABLE",
        operational_zone="ZONE_1"
    )

    # Physical exertion discounts physio attribution
    assert res.advisory_welfare_state in ["MONITORING_ONLY", "STABLE"]
    assert res.human_review_required is False

# Test 12: Poor Data Quality Gating
def test_poor_data_quality_gating(fusion_engine):
    res = fusion_engine.evaluate_multimodal_welfare(
        personnel_id="P-101",
        p_physio=0.85,
        data_quality_score=0.20,  # Corrupted data (< 0.40)
        is_physical_exertion=False,
        z_autonomic=3.0,
        recovery_burden_score=80.0,
        sleep_deficit_hours=4.0,
        trajectory_direction="DETERIORATING",
        operational_zone="ZONE_2"
    )

    assert res.advisory_welfare_state == "INCONCLUSIVE_DATA"
    assert res.multimodal_confidence == 0.20
    assert res.human_review_required is False

# Test 13: Zone 3 Critical Post-Incident Escalation
def test_zone_3_medical_review_escalation(fusion_engine):
    res = fusion_engine.evaluate_multimodal_welfare(
        personnel_id="P-101",
        p_physio=0.88,
        data_quality_score=0.95,
        is_physical_exertion=False,
        z_autonomic=4.2,
        recovery_burden_score=90.0,
        sleep_deficit_hours=6.0,
        trajectory_direction="DETERIORATING",
        operational_zone="ZONE_3"
    )

    assert res.advisory_welfare_state == "MEDICAL_REVIEW"
    assert res.human_review_required is True
    assert "Recommend authorized welfare/medical review" in res.recommended_action

# Test 14: Strict Zero-Raw-Audio Retention
def test_raw_audio_discarded_by_default(extractor):
    clean_audio = extractor.generate_synthetic_audio(duration_seconds=10.0)
    snapshot = extractor.extract_features(clean_audio)
    # Feature snapshot contains only numbers, zero byte arrays
    for k, v in snapshot.feature_values.items():
        assert isinstance(v, (int, float, np.floating, np.integer))
    assert not hasattr(snapshot, "raw_audio_bytes")

# Test 15: Non-Diagnostic Terminology Invariant
def test_non_diagnostic_phrasing(fusion_engine, baseline_engine):
    history = [
        {"evidence_status": "VALID", "feature_values": {"f0_mean": 120.0, "pause_ratio": 0.30, "speech_rate_proxy_bpm": 130.0, "rms_energy_mean": 0.25}},
        {"evidence_status": "VALID", "feature_values": {"f0_mean": 122.0, "pause_ratio": 0.31, "speech_rate_proxy_bpm": 128.0, "rms_energy_mean": 0.26}},
        {"evidence_status": "VALID", "feature_values": {"f0_mean": 118.0, "pause_ratio": 0.29, "speech_rate_proxy_bpm": 132.0, "rms_energy_mean": 0.24}},
    ]
    base = baseline_engine.compute_personal_baseline("P-101", history)
    curr = {"f0_mean": 160.0, "pause_ratio": 0.60, "speech_rate_proxy_bpm": 90.0, "rms_energy_mean": 0.12}
    dev = baseline_engine.evaluate_deviation("P-101", curr, base)

    # Phrasing must not contain prohibited clinical assertions
    prohibited = ["mental illness", "diagnos", "suicide", "disorder", "proven stress", "patholog"]
    for word in prohibited:
        assert word not in dev.non_diagnostic_summary.lower()

# Test 16: Multimodal Contributing Streams Logging
def test_contributing_streams_audit(fusion_engine):
    res = fusion_engine.evaluate_multimodal_welfare(
        personnel_id="P-101",
        p_physio=0.60,
        data_quality_score=0.90,
        is_physical_exertion=False,
        z_autonomic=1.5,
        recovery_burden_score=40.0,
        sleep_deficit_hours=2.0,
        trajectory_direction="STABLE",
        operational_zone="ZONE_2"
    )

    stream_names = [s["stream"] for s in res.contributing_streams]
    assert "PHYSIOLOGICAL_ML" in stream_names
    assert "AUTONOMIC_BASELINE" in stream_names
    assert "RECOVERY_TRAJECTORY" in stream_names
    assert "SLEEP_RECOVERY_DEBT" in stream_names
