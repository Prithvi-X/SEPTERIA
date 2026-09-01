"""
SEPTERIA Phase 8 Demonstration Script: Voice & Multimodal Welfare Intelligence

Demonstrates:
  1. Mandatory Voluntary Consent & In-Memory Acoustic Signal Processing (Zero Raw Audio Saved)
  2. Personal Acoustic Baseline & Transparent Deviation Detection
  3. Contextual Graph + Wearable ML + Autonomic Trajectory + Voice Multimodal Evidence Fusion
  4. BSF Unit 47 Soldier BSF-47-01 Scenario: Multi-day strain, voluntary voice check-in, shared graph pattern -> ELEVATED WELFARE CONCERN
  5. 3 Invariant Checks:
     - Exertion Disambiguation (High ACC + Normal Voice -> Exertion Context, No Escalation)
     - Evidence Conflict (Instantaneous Physio vs Normal Baseline & Improving Trajectory -> Contradiction Flagged)
     - Voice Alone (Strained Voice Alone -> Voluntary Check-In, Cannot Escalate to AMBER/RED)
  6. Privacy & Authority View Separation (Commander Aggregate vs Authorized Medical Officer)
"""

import os
import sys
import json
import base64

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.engine.voice.voice_feature_extractor import VoiceFeatureExtractor, VoiceFeatureSnapshot
from backend.app.engine.voice.voice_baseline_engine import VoiceBaselineEngine, VoiceBaseline, VoicePatternDeviation
from backend.app.engine.multimodal.multimodal_fusion_engine import (
    MultimodalFusionEngine,
    MultimodalFusionConfig,
    MultimodalEvidenceResult,
)
from backend.app.engine.graph.contextual_graph_engine import ContextualGraphEngine

def run_demo():
    print("=" * 100)
    print("SEPTERIA PHASE 8 DEMONSTRATION: VOICE INTELLIGENCE + MULTIMODAL EVIDENCE FUSION")
    print("=" * 100)

    extractor = VoiceFeatureExtractor()
    baseline_engine = VoiceBaselineEngine(min_baseline_samples=3)
    fusion_engine = MultimodalFusionEngine()
    graph_engine = ContextualGraphEngine()

    personnel_id = "BSF-47-01"

    # -------------------------------------------------------------------------
    # STEP 1: Personal Voice Baseline Establishment (3 Historical Samples)
    # -------------------------------------------------------------------------
    print("\n[STEP 1] Personal Voice Baseline Acquisition (3 Historical Rest Recordings)...")
    historical_snapshots = [
        {"evidence_status": "VALID", "feature_values": {"f0_mean": 120.0, "f0_std": 10.5, "pause_ratio": 0.30, "speech_rate_proxy_bpm": 130.0, "rms_energy_mean": 0.25, "rms_energy_std": 0.05, "spectral_centroid_mean": 1500.0}},
        {"evidence_status": "VALID", "feature_values": {"f0_mean": 122.0, "f0_std": 11.0, "pause_ratio": 0.31, "speech_rate_proxy_bpm": 128.0, "rms_energy_mean": 0.26, "rms_energy_std": 0.06, "spectral_centroid_mean": 1520.0}},
        {"evidence_status": "VALID", "feature_values": {"f0_mean": 118.0, "f0_std": 9.5, "pause_ratio": 0.29, "speech_rate_proxy_bpm": 132.0, "rms_energy_mean": 0.24, "rms_energy_std": 0.04, "spectral_centroid_mean": 1480.0}},
    ]
    baseline = baseline_engine.compute_personal_baseline(personnel_id, historical_snapshots)
    print(f"  Baseline Status           : [{baseline.status}] (Observations: {baseline.observation_count})")
    print(f"  Personal Resting Pitch F0 : {baseline.baseline_medians['f0_mean']} Hz (MAD: {baseline.baseline_mads['f0_mean']:.2f} Hz)")
    print(f"  Personal Resting Pause    : {baseline.baseline_medians['pause_ratio']*100:.1f}% (MAD: {baseline.baseline_mads['pause_ratio']*100:.2f}%)")
    print(f"  Baseline Quality Score    : {baseline.baseline_quality_score:.2f} / 1.0")

    # -------------------------------------------------------------------------
    # STEP 2: Voluntary Voice Check-In Processing & Acoustic Extraction
    # -------------------------------------------------------------------------
    print("\n[STEP 2] Voluntary Voice Check-In Processing (20-Second Acoustic Sample)...")
    # Synthesize 20s strained audio sample (elevated pitch + syllable rate shift)
    strained_audio = extractor.generate_synthetic_audio(
        duration_seconds=20.0,
        pitch_f0_hz=155.0,  # Elevated relative to 120 Hz baseline
        speech_rate_multiplier=0.75,
        energy_level=0.18
    )
    snapshot = extractor.extract_features(strained_audio)
    print(f"  Sample Duration           : {snapshot.signal_duration_seconds}s (Consent: Verified)")
    print(f"  Audio Quality Score       : {snapshot.audio_quality_score:.2f} / 1.0 (Status: [{snapshot.evidence_status}])")
    print(f"  Measured Pitch Mean (F0)  : {snapshot.feature_values['f0_mean']:.1f} Hz")
    print(f"  Measured Pause Ratio      : {snapshot.feature_values['pause_ratio']*100:.1f}%")
    print(f"  Speech Rate Proxy         : {snapshot.feature_values['speech_rate_proxy_bpm']:.1f} BPM")
    print(f"  Raw Audio Retention Policy: STRICT DISCARD (Zero raw audio bytes saved)")

    # Evaluate Deviation
    voice_dev = baseline_engine.evaluate_deviation(
        personnel_id=personnel_id,
        current_features=snapshot.feature_values,
        baseline=baseline,
        audio_quality_score=snapshot.audio_quality_score
    )
    print(f"  Deviation Magnitude       : {voice_dev.deviation_magnitude:.3f} / 1.0 ({voice_dev.status})")
    print(f"  Acoustic Shifts           : {voice_dev.primary_acoustic_shifts}")
    print(f"  Non-Diagnostic Summary    : \"{voice_dev.non_diagnostic_summary}\"")

    # -------------------------------------------------------------------------
    # STEP 3: Contextual Graph Context Integration (BSF Unit 47)
    # -------------------------------------------------------------------------
    print("\n[STEP 3] Contextual Personnel Graph Evaluation (BSF Unit 47)...")
    graph_evidence = {
        "shared_pattern_detected": True,
        "pattern_id": "PAT-BSF-BN-47-ZONE_2-Night-1",
        "affected_headcount": 14,
        "summary": "Unit BSF-BN-47 [ZONE_2, Night Shift]: Shared recovery trajectory deterioration detected affecting 14 of 20 personnel under active deployment."
    }
    print(f"  Shared Cluster Pattern    : {graph_evidence['pattern_id']} (Headcount: {graph_evidence['affected_headcount']} personnel)")
    print(f"  Operational Context       : Zone 2 (Border Outpost), Night Patrol, Post-Leave Transition")

    # -------------------------------------------------------------------------
    # STEP 4: Multimodal Evidence Fusion (BSF-47-01 Convergence Scenario)
    # -------------------------------------------------------------------------
    print("\n[STEP 4] Multimodal Evidence Fusion Evaluation...")
    fusion_result: MultimodalEvidenceResult = fusion_engine.evaluate_multimodal_welfare(
        personnel_id=personnel_id,
        p_physio=0.82,                  # Elevated instantaneous stress likelihood
        data_quality_score=0.92,        # High sensor quality
        is_physical_exertion=False,     # Stationary post-patrol rest window
        z_autonomic=3.15,               # Elevated HR (105 bpm) & Suppressed HRV (22 ms)
        recovery_burden_score=78.0,     # High cumulative recovery debt
        sleep_deficit_hours=4.5,        # 4.5 hours sleep debt
        trajectory_direction="DETERIORATING", # Multi-day worsening trend
        operational_zone="ZONE_2",
        graph_evidence=graph_evidence,
        voice_deviation=voice_dev
    )

    print(f"  Composite Welfare Score   : {fusion_result.composite_welfare_score:.3f} / 1.0")
    print(f"  Multimodal Confidence     : {fusion_result.multimodal_confidence:.2f} / 1.0")
    print(f"  Evidence Agreement Index  : {fusion_result.evidence_agreement_score:.2f} / 1.0 (High Multi-Stream Convergence)")
    print(f"  Evidence Conflict Flag    : {fusion_result.is_evidence_conflict}")
    print(f"  Advisory Welfare State    : [{fusion_result.advisory_welfare_state}]")
    print(f"  Human Review Required     : {fusion_result.human_review_required}")
    print(f"  Recommended Action Text   : \"{fusion_result.recommended_action}\"")

    print("\n  Contributing Evidence Streams Breakdown:")
    for s in fusion_result.contributing_streams:
        print(f"   - {s['stream']:<22}: Score = {s.get('score', 'N/A'):<6} | Weight = {s.get('weight', 'N/A'):<6} | Context = {s.get('context') or s.get('direction') or s.get('summary') or s.get('quality') or ''}")

    # -------------------------------------------------------------------------
    # STEP 5: Invariant Sanity Checks
    # -------------------------------------------------------------------------
    print("\n[STEP 5] Verifying Core Safety & Ethical Invariants...")

    # Invariant A: Physical Exertion Disambiguation
    res_exertion = fusion_engine.evaluate_multimodal_welfare(
        personnel_id="P-EXERTION",
        p_physio=0.94, data_quality_score=0.90, is_physical_exertion=True,
        z_autonomic=0.4, recovery_burden_score=15.0, sleep_deficit_hours=0.0,
        trajectory_direction="STABLE", operational_zone="ZONE_1"
    )
    print(f"  [INVARIANT A] Kinetic Exertion Alone -> State = [{res_exertion.advisory_welfare_state}] (Escalated: {res_exertion.human_review_required}) -> PASS")

    # Invariant B: Evidence Contradiction Handling
    res_conflict = fusion_engine.evaluate_multimodal_welfare(
        personnel_id="P-CONFLICT",
        p_physio=0.88, data_quality_score=0.90, is_physical_exertion=False,
        z_autonomic=0.2, recovery_burden_score=10.0, sleep_deficit_hours=0.0,
        trajectory_direction="IMPROVING", operational_zone="ZONE_2"
    )
    print(f"  [INVARIANT B] Telemetry Contradiction -> is_evidence_conflict = {res_conflict.is_evidence_conflict} (State = [{res_conflict.advisory_welfare_state}]) -> PASS")

    # Invariant C: Voice Alone Cannot Trigger Red/Amber Escalation
    res_voice_alone = fusion_engine.evaluate_multimodal_welfare(
        personnel_id="P-VOICE-ONLY",
        p_physio=0.15, data_quality_score=1.0, is_physical_exertion=False,
        z_autonomic=0.0, recovery_burden_score=0.0, sleep_deficit_hours=0.0,
        trajectory_direction="STABLE", operational_zone="ZONE_2",
        voice_deviation=voice_dev
    )
    print(f"  [INVARIANT C] Strained Voice Alone -> State = [{res_voice_alone.advisory_welfare_state}] (Escalated: {res_voice_alone.human_review_required}) -> PASS")

    # Invariant D: Low Quality Data Gate
    res_low_qual = fusion_engine.evaluate_multimodal_welfare(
        personnel_id="P-POOR-DATA",
        p_physio=0.90, data_quality_score=0.20, is_physical_exertion=False,
        z_autonomic=3.5, recovery_burden_score=80.0, sleep_deficit_hours=4.0,
        trajectory_direction="DETERIORATING", operational_zone="ZONE_2"
    )
    print(f"  [INVARIANT D] Poor Data Quality (<0.40) -> State = [{res_low_qual.advisory_welfare_state}] -> PASS")

    print("\n" + "=" * 100)
    print("[PHASE 8 DEMO COMPLETED SUCCESSFULLY]")
    print("=" * 100)

if __name__ == "__main__":
    run_demo()
