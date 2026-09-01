from typing import Dict, Any, List, Optional

class ContextualAssessment:
    def __init__(
        self,
        attribution_summary: str,
        motion_context: str,
        confidence_adjustment: float,
        discrepancies: List[str],
    ):
        self.attribution_summary = attribution_summary
        self.motion_context = motion_context
        self.confidence_adjustment = confidence_adjustment
        self.discrepancies = discrepancies

class ContradictionDetector:
    """
    Evaluates multimodal alignment across physiological observations, motion context,
    voluntary wellness reports, and authoritative operational environment.

    Scientific Principle:
    Physiological/contextual rules adjust attribution and confidence; they do NOT make
    definitive psychological-stress conclusions.
    """

    @staticmethod
    def assess(
        hr: Optional[float],
        hrv: Optional[float],
        activity: float,
        sleep: Optional[float] = None,
        wellness_stress: Optional[int] = None,
        operational_zone: Optional[str] = None,
        ambient_temp: Optional[float] = None,
    ) -> ContextualAssessment:
        discrepancies: List[str] = []
        confidence_adj = 1.0
        hr_val = hr or 70.0
        act_val = activity or 0.0

        # 1. Physical Exertion vs. Elevated Heart Rate
        if hr_val >= 110.0 and act_val >= 6000.0:
            summary = "Physiological elevation is consistent with physical exertion; psychological attribution reduced."
            confidence_adj = 0.65
            if ambient_temp and ambient_temp >= 40.0:
                discrepancies.append(f"High environmental heat ({ambient_temp:.1f}°C) compounds cardiovascular exertion.")
        elif hr_val >= 100.0 and act_val < 3000.0:
            summary = "Physiological elevation without physical exertion; potential unexplained physiological deviation."
            confidence_adj = 0.90
            discrepancies.append("Elevated heart rate observed during low-motion interval.")
            if hrv and hrv < 35.0:
                discrepancies.append("Concurrent depressed autonomic HRV indicates possible physiological strain.")
        elif hr_val < 85.0 and act_val < 3000.0:
            summary = "Physiological telemetry within expected baseline resting range."
            confidence_adj = 1.0
        else:
            summary = "Routine operational cardiovascular dynamics observed."
            confidence_adj = 1.0

        # 2. Voluntary Check-in Discrepancy Checks
        if wellness_stress is not None:
            if wellness_stress >= 4 and hr_val < 70.0 and (hrv or 60.0) > 55.0:
                discrepancies.append("Discrepancy: Self-reported elevated stress while autonomic physiological indicators remain stable.")
            elif wellness_stress <= 2 and hr_val > 105.0 and act_val < 3000.0:
                discrepancies.append("Discrepancy: Self-reported low stress despite elevated resting cardiovascular telemetry.")

        # 3. Sleep Context Checks
        if sleep is not None and sleep < 5.0:
            discrepancies.append(f"Restorative sleep duration ({sleep:.1f}h) below standard physiological baseline.")

        motion_label = "EXERTIONAL" if act_val >= 8000.0 else "MODERATE" if act_val >= 3000.0 else "LOW"

        return ContextualAssessment(
            attribution_summary=summary,
            motion_context=motion_label,
            confidence_adjustment=confidence_adj,
            discrepancies=discrepancies,
        )
