from typing import Dict, Any, List, Tuple
from shared.constants.evidence import SQIStatus, EvidenceStatus

class SignalQualityResult:
    def __init__(self, sqi_status: str, score: float, evidence_status: str, reasons: List[str]):
        self.sqi_status = sqi_status
        self.score = score
        self.evidence_status = evidence_status
        self.reasons = reasons

class SignalQualityEngine:
    """
    Prototype Signal Quality Index (SQI) evaluator.
    Determines whether an incoming observation is GOOD, FAIR, POOR, or MISSING,
    and assigns appropriate evidence status (OBSERVED, DERIVED, INFERRED, UNCERTAIN).
    
    *Note: This is an algorithmic quality gate designed for prototype triage and requires
    device-specific sensor calibration in production deployments.*
    """

    @classmethod
    def evaluate(cls, record: Dict[str, Any], validator_warnings: List[str] = None) -> SignalQualityResult:
        warnings = validator_warnings or []
        reasons: List[str] = []
        score = 1.0

        hr = record.get("hr")
        hrv = record.get("hrv")
        raw_sq = float(record.get("signal_quality", 1.0))
        motion = record.get("activity", 0.0)

        # 1. Total Missingness Check
        if hr is None and hrv is None:
            return SignalQualityResult(
                sqi_status=SQIStatus.MISSING.value,
                score=0.0,
                evidence_status=EvidenceStatus.UNCERTAIN.value,
                reasons=["Both primary signals (HR and HRV) are absent."],
            )

        # 2. Hardware / Sensor Reported Signal Quality
        if raw_sq < 0.4:
            score -= 0.6
            reasons.append(f"Hardware sensor reported severely degraded PPG contact quality ({raw_sq:.2f}).")
        elif raw_sq < 0.6:
            score -= 0.35
            reasons.append(f"Hardware sensor reported low PPG contact quality ({raw_sq:.2f}).")
        elif raw_sq < 0.8:
            score -= 0.2
            reasons.append(f"Minor PPG optical signal noise reported ({raw_sq:.2f}).")

        # 3. Motion Artifact Penalization
        if motion > 9000.0:
            score -= 0.15
            reasons.append("High physical motion introduces potential optical PPG artifact.")

        # 4. Validator Discontinuity Warnings
        if warnings:
            score -= (0.15 * len(warnings))
            reasons.extend(warnings)

        # 5. Inferred / Imputed Check
        is_inferred = record.get("evidence_status") == EvidenceStatus.INFERRED.value or record.get("is_reconstructed", False)
        if is_inferred:
            score = min(score, 0.75)
            reasons.append("Record generated via conservative mathematical interpolation (INFERRED).")

        # Clamp Score
        score = max(0.0, min(1.0, score))

        # Determine Categorical Status
        if is_inferred:
            sqi_status = SQIStatus.FAIR.value
            ev_status = EvidenceStatus.INFERRED.value
        elif score >= 0.80:
            sqi_status = SQIStatus.GOOD.value
            ev_status = EvidenceStatus.OBSERVED.value
        elif score >= 0.50:
            sqi_status = SQIStatus.FAIR.value
            ev_status = EvidenceStatus.OBSERVED.value
        elif score > 0.0:
            sqi_status = SQIStatus.POOR.value
            ev_status = EvidenceStatus.UNCERTAIN.value
        else:
            sqi_status = SQIStatus.MISSING.value
            ev_status = EvidenceStatus.UNCERTAIN.value

        return SignalQualityResult(
            sqi_status=sqi_status,
            score=round(score, 2),
            evidence_status=ev_status,
            reasons=reasons,
        )
