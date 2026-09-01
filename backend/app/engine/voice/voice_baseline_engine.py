"""
SEPTERIA Personal Voice Baseline & Deviation Engine (Phase 8)

Non-Diagnostic Acoustic Pattern Analysis:
- Compares current voluntary voice check-in against that person's own baseline.
- Minimum 3 historical voice recordings required to establish a valid personal baseline.
- Transparent deviation metrics (median absolute deviation z-scores).
- Outputs non-diagnostic deviation indicators; never claims voice proves clinical stress.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import numpy as np

@dataclass
class VoiceBaseline:
    personnel_id: str
    baseline_medians: Dict[str, float]
    baseline_mads: Dict[str, float]
    observation_count: int
    baseline_quality_score: float
    is_established: bool
    status: str  # VOICE_BASELINE_ESTABLISHED or VOICE_BASELINE_UNAVAILABLE
    last_updated: str

@dataclass
class VoicePatternDeviation:
    personnel_id: str
    has_valid_baseline: bool
    status: str  # VOICE_PATTERN_DEVIATION, WITHIN_PERSONAL_BASELINE, VOICE_BASELINE_UNAVAILABLE, VOICE_INCONCLUSIVE
    deviation_magnitude: float  # [0.0, 1.0]
    direction: str              # ACOUSTIC_ELEVATION, ACOUSTIC_SUPPRESSION, WITHIN_NORMAL_DISPERSION, INCONCLUSIVE
    z_scores: Dict[str, float]
    primary_acoustic_shifts: List[str]
    evidence_quality: float     # [0.0, 1.0] based on audio quality & baseline sample depth
    non_diagnostic_summary: str
    timestamp: str

class VoiceBaselineEngine:
    """
    Computes personal resting voice baselines and acoustic deviations for individual uniformed personnel.
    """
    def __init__(self, min_baseline_samples: int = 3):
        self.min_baseline_samples = min_baseline_samples
        # Primary acoustic markers for longitudinal comparison
        self.tracking_metrics = [
            "f0_mean",
            "f0_std",
            "f0_iqr",
            "pause_ratio",
            "mean_pause_duration_s",
            "speech_rate_proxy_bpm",
            "rms_energy_mean",
            "rms_energy_std",
            "spectral_centroid_mean"
        ]

    def compute_personal_baseline(
        self,
        personnel_id: str,
        historical_snapshots: List[Dict[str, Any]]
    ) -> VoiceBaseline:
        """
        Computes robust medians and MADs from historical valid voice check-in snapshots.
        """
        now_ts = datetime.utcnow().isoformat()

        valid_snapshots = [
            s for s in historical_snapshots
            if s.get("evidence_status") == "VALID" and s.get("feature_values")
        ]

        count = len(valid_snapshots)
        if count < self.min_baseline_samples:
            return VoiceBaseline(
                personnel_id=personnel_id,
                baseline_medians={},
                baseline_mads={},
                observation_count=count,
                baseline_quality_score=float(count / self.min_baseline_samples) * 0.5,
                is_established=False,
                status="VOICE_BASELINE_UNAVAILABLE",
                last_updated=now_ts
            )

        medians = {}
        mads = {}
        for metric in self.tracking_metrics:
            values = [
                s["feature_values"][metric]
                for s in valid_snapshots
                if metric in s.get("feature_values", {})
            ]
            if len(values) >= self.min_baseline_samples:
                med = float(np.median(values))
                mad = float(np.median(np.abs(np.array(values) - med)))
                medians[metric] = med
                mads[metric] = max(1e-4, mad)

        # Baseline quality scales with number of historical samples (saturates at 10)
        quality = min(1.0, 0.6 + 0.04 * count)

        return VoiceBaseline(
            personnel_id=personnel_id,
            baseline_medians=medians,
            baseline_mads=mads,
            observation_count=count,
            baseline_quality_score=float(quality),
            is_established=True,
            status="VOICE_BASELINE_ESTABLISHED",
            last_updated=now_ts
        )

    def evaluate_deviation(
        self,
        personnel_id: str,
        current_features: Dict[str, float],
        baseline: VoiceBaseline,
        audio_quality_score: float = 1.0
    ) -> VoicePatternDeviation:
        """
        Evaluates current acoustic features relative to personal baseline.
        """
        now_ts = datetime.utcnow().isoformat()

        if not baseline.is_established or not baseline.baseline_medians:
            return VoicePatternDeviation(
                personnel_id=personnel_id,
                has_valid_baseline=False,
                status="VOICE_BASELINE_UNAVAILABLE",
                deviation_magnitude=0.0,
                direction="INCONCLUSIVE",
                z_scores={},
                primary_acoustic_shifts=[],
                evidence_quality=0.0,
                non_diagnostic_summary="Insufficient historical voice recordings (< 3 samples) to calculate a personal baseline.",
                timestamp=now_ts
            )

        if not current_features or audio_quality_score < 0.35:
            return VoicePatternDeviation(
                personnel_id=personnel_id,
                has_valid_baseline=True,
                status="VOICE_INCONCLUSIVE",
                deviation_magnitude=0.0,
                direction="INCONCLUSIVE",
                z_scores={},
                primary_acoustic_shifts=[],
                evidence_quality=audio_quality_score,
                non_diagnostic_summary="Audio recording quality was insufficient for conclusive acoustic comparison.",
                timestamp=now_ts
            )

        # Compute robust z-scores for key acoustic metrics
        z_scores = {}
        shifts = []

        for metric in self.tracking_metrics:
            if metric in current_features and metric in baseline.baseline_medians:
                val = current_features[metric]
                med = baseline.baseline_medians[metric]
                mad = baseline.baseline_mads[metric]
                # Normal consistency scale factor for MAD is 1.4826
                z = (val - med) / (1.4826 * mad + 1e-4)
                z_scores[metric] = float(np.clip(z, -6.0, 6.0))

                if abs(z) >= 2.0:
                    dir_text = "elevated" if z > 0 else "reduced"
                    shifts.append(f"{metric.replace('_', ' ').title()} {dir_text} (|z| = {abs(z):.1f})")

        # Composite acoustic deviation magnitude using core indicators:
        # F0 (pitch), Pause ratio, Speech rate, Energy
        z_f0 = abs(z_scores.get("f0_mean", 0.0))
        z_pause = abs(z_scores.get("pause_ratio", 0.0))
        z_rate = abs(z_scores.get("speech_rate_proxy_bpm", 0.0))
        z_energy = abs(z_scores.get("rms_energy_mean", 0.0))
        z_f0_var = abs(z_scores.get("f0_std", 0.0))

        # Composite weighted z-score
        composite_z = 0.25 * z_f0 + 0.25 * z_pause + 0.20 * z_rate + 0.15 * z_energy + 0.15 * z_f0_var
        # Map into [0.0, 1.0] via bounded saturation function
        deviation_magnitude = float(np.tanh(composite_z / 2.5))

        # Direction classification
        if composite_z < 1.2:
            direction = "WITHIN_NORMAL_DISPERSION"
            status = "WITHIN_PERSONAL_BASELINE"
            summary = "Voice acoustic markers are congruent with your established personal baseline."
        elif z_f0 > 1.5 or z_pause > 1.5:
            direction = "ACOUSTIC_ELEVATION"
            status = "VOICE_PATTERN_DEVIATION"
            summary = "Voice acoustic markers show noticeable variance (pitch / pause dynamics) relative to your personal baseline."
        elif z_energy < -1.5 or z_f0_var < -1.5:
            direction = "ACOUSTIC_SUPPRESSION"
            status = "VOICE_PATTERN_DEVIATION"
            summary = "Voice acoustic markers show flatter dynamics or lower energy relative to your personal baseline."
        else:
            direction = "MODERATE_VARIANCE"
            status = "VOICE_PATTERN_DEVIATION"
            summary = "Voice acoustic markers show moderate dispersion relative to your personal baseline."

        evidence_quality = float(audio_quality_score * baseline.baseline_quality_score)

        return VoicePatternDeviation(
            personnel_id=personnel_id,
            has_valid_baseline=True,
            status=status,
            deviation_magnitude=deviation_magnitude,
            direction=direction,
            z_scores=z_scores,
            primary_acoustic_shifts=shifts,
            evidence_quality=evidence_quality,
            non_diagnostic_summary=summary,
            timestamp=now_ts
        )
