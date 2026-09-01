"""
SEPTERIA Multimodal Welfare Intelligence & Evidence Fusion Engine (Phase 8)

Integrates:
  1. Layer 1: XGBoost Physiological Stress Probability (P_physio)
  2. Layer 2: Personal Baseline Deviations, Exertion Disambiguation, Zone Gates
  3. Layer 5: Autonomic Trajectory, Recovery Burden, Sleep Debt
  4. Phase 7: Contextual Personnel Graph Evidence (Shared Cluster Deterioration)
  5. Phase 8: Optional Voluntary Voice Pattern Deviation & Acoustic Quality

Invariants:
  - Voice is an optional, non-diagnostic corroborating stream; voice ALONE never triggers AMBER or RED.
  - Transparent rule-based evidence fusion with explicit agreement and conflict detection.
  - All fusion weights and parameters are configurable and explicitly provisional.
  - Non-punitive, human-in-the-loop advisory recommendations only.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import numpy as np

from backend.app.engine.voice.voice_baseline_engine import VoicePatternDeviation

@dataclass
class MultimodalFusionConfig:
    config_version: str = "v1.0.0-PROTOTYPE"
    # Evidence Stream Weights
    w_physio: float = 0.35
    w_baseline: float = 0.25
    w_trajectory: float = 0.15
    w_sleep: float = 0.10
    w_graph: float = 0.05
    w_voice: float = 0.10

    # Decision Thresholds
    welfare_check_threshold: float = 0.55
    medical_review_threshold: float = 0.75
    conflict_penalty_factor: float = 0.40
    min_data_quality_gate: float = 0.40

    is_provisional_prototype: bool = True
    regulatory_note: str = (
        "Multimodal fusion outputs are evidence-based decision-support indicators. "
        "They do not constitute medical, psychiatric, or autonomous operational directives."
    )

@dataclass
class MultimodalEvidenceResult:
    personnel_id: Optional[str]
    advisory_welfare_state: str  # STABLE, MONITORING_ONLY, VOLUNTARY_CHECKIN, WELFARE_CHECK, MEDICAL_REVIEW, INCONCLUSIVE_DATA
    composite_welfare_score: float  # [0.0, 1.0]
    multimodal_confidence: float    # [0.0, 1.0]
    evidence_agreement_score: float # [0.0, 1.0]
    is_evidence_conflict: bool
    conflict_details: Optional[str]
    contributing_streams: List[Dict[str, Any]]
    voice_evidence_included: bool
    voice_summary: Optional[str]
    graph_evidence_included: bool
    graph_summary: Optional[str]
    recommended_action: str
    human_review_required: bool
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class MultimodalFusionEngine:
    """
    Transparent Multimodal Evidence Fusion Service.
    Corroborates physiological, autonomic baseline, operational context, graph, and voice evidence.
    """
    def __init__(self, config: Optional[MultimodalFusionConfig] = None):
        self.config = config or MultimodalFusionConfig()

    def evaluate_multimodal_welfare(
        self,
        personnel_id: Optional[str],
        p_physio: float,
        data_quality_score: float,
        is_physical_exertion: bool,
        z_autonomic: float,
        recovery_burden_score: float,
        sleep_deficit_hours: float,
        trajectory_direction: str,  # IMPROVING, STABLE, DETERIORATING
        operational_zone: str,      # ZONE_1, ZONE_2, ZONE_3
        graph_evidence: Optional[Dict[str, Any]] = None,
        voice_deviation: Optional[VoicePatternDeviation] = None,
    ) -> MultimodalEvidenceResult:
        """
        Executes multimodal evidence convergence and conflict arbitration.
        """
        cfg = self.config

        # 1. Gating check: Poor data quality -> INCONCLUSIVE_DATA
        if data_quality_score < cfg.min_data_quality_gate:
            return MultimodalEvidenceResult(
                personnel_id=personnel_id,
                advisory_welfare_state="INCONCLUSIVE_DATA",
                composite_welfare_score=0.0,
                multimodal_confidence=data_quality_score,
                evidence_agreement_score=0.0,
                is_evidence_conflict=False,
                conflict_details=None,
                contributing_streams=[{"stream": "DATA_QUALITY", "status": "INSUFFICIENT_TELEMETRY"}],
                voice_evidence_included=False,
                voice_summary=None,
                graph_evidence_included=False,
                graph_summary=None,
                recommended_action="Telemetry quality insufficient for multimodal assessment; maintain routine passive monitoring.",
                human_review_required=False
            )

        # 2. Extract Individual Stream Evidence Scores [0.0, 1.0] (0 = Calm/Recovered, 1 = Elevated Strain)
        # Physio evidence
        e_physio = float(np.clip(p_physio, 0.0, 1.0))
        if is_physical_exertion:
            # Physical exertion discounts physiological attribution to psychological stress
            e_physio = e_physio * 0.40

        # Baseline autonomic deviation score
        # z_autonomic mapped to [0.0, 1.0]: 0 -> 0.0, 2.0 -> 0.63, 4.0 -> 0.95
        e_baseline = float(np.tanh(max(0.0, z_autonomic) / 2.0))

        # Trajectory evidence
        if trajectory_direction == "DETERIORATING":
            e_trajectory = 0.85
        elif trajectory_direction == "STABLE":
            e_trajectory = 0.35
        else:  # IMPROVING
            e_trajectory = 0.10

        # Sleep deficit evidence
        e_sleep = float(np.clip(sleep_deficit_hours / 6.0, 0.0, 1.0))

        # Recovery burden evidence
        e_recovery = float(np.clip(recovery_burden_score / 100.0, 0.0, 1.0))
        # Composite physiological/lifestyle strain
        e_lifestyle = 0.6 * e_sleep + 0.4 * e_recovery

        # Graph Context Evidence (Shared cohort distress)
        has_graph = graph_evidence is not None and graph_evidence.get("shared_pattern_detected", False)
        e_graph = 0.75 if has_graph else 0.20
        graph_summary = graph_evidence.get("summary") if graph_evidence else None

        # Voice Evidence
        has_voice = (
            voice_deviation is not None
            and voice_deviation.has_valid_baseline
            and voice_deviation.status == "VOICE_PATTERN_DEVIATION"
            and voice_deviation.evidence_quality >= 0.35
        )
        if has_voice:
            e_voice = float(np.clip(voice_deviation.deviation_magnitude, 0.0, 1.0))
            voice_summary = voice_deviation.non_diagnostic_summary
        else:
            e_voice = 0.0
            voice_summary = voice_deviation.non_diagnostic_summary if voice_deviation else "No voluntary voice sample provided."

        # 3. Detect Evidence Conflict / Contradiction
        # Conflict 1: High physio but normal/improving baseline, normal voice, and stable/improving trajectory
        is_conflict = False
        conflict_reasons = []

        if p_physio >= 0.70 and not is_physical_exertion:
            if trajectory_direction == "IMPROVING" and z_autonomic < 1.0:
                is_conflict = True
                conflict_reasons.append("Elevated instantaneous physiology contradicts improving autonomic multi-day trajectory.")
            if has_voice and e_voice < 0.25 and z_autonomic < 0.8:
                is_conflict = True
                conflict_reasons.append("Elevated instantaneous physiology contradicts baseline-congruent acoustic and autonomic indicators.")

        if is_physical_exertion and p_physio >= 0.60:
            conflict_reasons.append("High motion energy indicates physical exertion context; physiological activation is discounted.")

        conflict_details = "; ".join(conflict_reasons) if conflict_reasons else None

        # 4. Compute Dynamic Weights based on available streams
        weights = {
            "physio": cfg.w_physio,
            "baseline": cfg.w_baseline,
            "trajectory": cfg.w_trajectory,
            "sleep": cfg.w_sleep,
            "graph": cfg.w_graph if has_graph else 0.0,
            "voice": cfg.w_voice if has_voice else 0.0,
        }
        total_w = sum(weights.values())
        norm_weights = {k: v / total_w for k, v in weights.items()}

        # 5. Composite Welfare Evidence Score
        score = (
            norm_weights["physio"] * e_physio +
            norm_weights["baseline"] * e_baseline +
            norm_weights["trajectory"] * e_trajectory +
            norm_weights["sleep"] * e_lifestyle +
            norm_weights["graph"] * e_graph +
            norm_weights["voice"] * e_voice
        )

        # Apply contradiction penalty if conflict detected
        if is_conflict:
            score = score * (1.0 - cfg.conflict_penalty_factor)

        composite_score = float(np.clip(score, 0.0, 1.0))

        # 6. Evidence Agreement & Confidence Calculation
        active_evidence_scores = [e_physio, e_baseline, e_trajectory, e_lifestyle]
        if has_graph:
            active_evidence_scores.append(e_graph)
        if has_voice:
            active_evidence_scores.append(e_voice)

        # Agreement: standard deviation of active evidence streams (lower std = higher agreement)
        ev_std = float(np.std(active_evidence_scores))
        agreement_score = float(np.clip(1.0 - 2.0 * ev_std, 0.1, 1.0))

        # Multimodal Confidence: scales with data quality, sample depth, and agreement
        voice_qual = voice_deviation.evidence_quality if voice_deviation else 0.5
        confidence = (
            0.40 * data_quality_score +
            0.30 * agreement_score +
            0.15 * (1.0 if has_voice else 0.6) +
            0.15 * (0.5 if is_conflict else 1.0)
        )
        multimodal_confidence = float(np.clip(confidence, 0.2, 0.98))

        # 7. Contributing Streams Logging
        contributing_streams = [
            {"stream": "PHYSIOLOGICAL_ML", "score": round(e_physio, 3), "weight": round(norm_weights["physio"], 3), "context": "Physical Exertion Discounted" if is_physical_exertion else "Standard Attribution"},
            {"stream": "AUTONOMIC_BASELINE", "score": round(e_baseline, 3), "weight": round(norm_weights["baseline"], 3), "z_autonomic": round(z_autonomic, 2)},
            {"stream": "RECOVERY_TRAJECTORY", "score": round(e_trajectory, 3), "weight": round(norm_weights["trajectory"], 3), "direction": trajectory_direction},
            {"stream": "SLEEP_RECOVERY_DEBT", "score": round(e_lifestyle, 3), "weight": round(norm_weights["sleep"], 3), "sleep_deficit_hours": sleep_deficit_hours},
        ]
        if has_graph:
            contributing_streams.append({"stream": "CONTEXTUAL_GRAPH", "score": round(e_graph, 3), "weight": round(norm_weights["graph"], 3), "summary": graph_summary})
        if has_voice:
            contributing_streams.append({"stream": "VOLUNTARY_VOICE", "score": round(e_voice, 3), "weight": round(norm_weights["voice"], 3), "quality": round(voice_qual, 2)})

        # 8. State Classification & Advisory Recommendations
        # Gating invariant: Voice alone CANNOT trigger WELFARE_CHECK or MEDICAL_REVIEW
        has_corroborating_wearable_strain = (e_baseline >= 0.40 or e_trajectory >= 0.60 or e_lifestyle >= 0.50)

        if operational_zone == "ZONE_3" and composite_score >= cfg.medical_review_threshold and has_corroborating_wearable_strain:
            state = "MEDICAL_REVIEW"
            action = "Recommend authorized welfare/medical review by Unit Medical Officer / Psychologist (Critical recovery debt in Zone 3)."
            human_review = True
        elif composite_score >= cfg.welfare_check_threshold and has_corroborating_wearable_strain:
            state = "WELFARE_CHECK"
            action = "Recommend authorized unit welfare check (Corroborating multi-stream strain across baseline, recovery, and operational indicators)."
            human_review = True
        elif composite_score >= 0.35 or (has_voice and e_voice >= 0.50):
            state = "VOLUNTARY_CHECKIN"
            action = "Consider voluntary wellness check-in and shift rest opportunity."
            human_review = False
        elif composite_score >= 0.20:
            state = "MONITORING_ONLY"
            action = "Maintain routine passive monitoring."
            human_review = False
        else:
            state = "STABLE"
            action = "Continue routine monitoring."
            human_review = False

        return MultimodalEvidenceResult(
            personnel_id=personnel_id,
            advisory_welfare_state=state,
            composite_welfare_score=round(composite_score, 3),
            multimodal_confidence=round(multimodal_confidence, 3),
            evidence_agreement_score=round(agreement_score, 3),
            is_evidence_conflict=is_conflict,
            conflict_details=conflict_details,
            contributing_streams=contributing_streams,
            voice_evidence_included=has_voice,
            voice_summary=voice_summary,
            graph_evidence_included=has_graph,
            graph_summary=graph_summary,
            recommended_action=action,
            human_review_required=human_review
        )
