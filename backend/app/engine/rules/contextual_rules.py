"""Contextual Interpretation Rules Engine for SEPTERIA.

Applies transparent rule-based contextual interpretations.
Strictly abides by scientific boundaries (User Mandate & Refinements):
- Physiological elevation during exertion -> psychological attribution reduced.
- Rules adjust attribution and confidence; they never formulate definitive clinical diagnoses.
"""
from typing import Dict, Any

class ContextualRulesEngine:
    @staticmethod
    def formulate_attribution(
        hr_elevated: bool,
        motion_context: str,
        hrv_suppressed: bool,
        sleep_deficit: bool,
        sqi_status: str = "GOOD",
    ) -> Dict[str, Any]:
        """Formulates explainable contextual attribution."""
        if sqi_status in ("POOR", "MISSING"):
            return {
                "summary": "Signal quality degraded; physiological attribution confidence reduced.",
                "confidence": "LOW",
                "is_exertion_explained": False,
            }

        if hr_elevated and motion_context in ("HIGH", "EXERTIONAL"):
            return {
                "summary": "Physiological elevation is consistent with physical exertion; psychological attribution reduced.",
                "confidence": "HIGH",
                "is_exertion_explained": True,
            }

        if hr_elevated and motion_context == "LOW" and (hrv_suppressed or sleep_deficit):
            return {
                "summary": "Physiological elevation without physical exertion; potential unexplained physiological deviation.",
                "confidence": "MODERATE",
                "is_exertion_explained": False,
            }

        return {
            "summary": "Physiological telemetry within expected baseline resting range.",
            "confidence": "HIGH",
            "is_exertion_explained": False,
        }
