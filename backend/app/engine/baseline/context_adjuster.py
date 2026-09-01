"""Context-Conditioned Baseline Adjustment Module.

Modifies baseline expectations dynamically based on current operational context
(e.g., Night Shift, High Heat / Altitude, Rest Day vs High-Intensity Tactical Duty).
"""
from typing import Dict, Any, Optional

class ContextAdjuster:
    @staticmethod
    def adjust_expected_baseline(
        metric: str,
        baseline_median: float,
        operational_zone: Optional[str] = None,
        duty_type: Optional[str] = None,
        shift: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Calculates context-adjusted expected baseline value and explanation."""
        adjusted = baseline_median
        modifiers = []

        # 1. Shift context
        if shift and "Night" in shift:
            if metric == "sleep_hours":
                adjusted = max(4.0, baseline_median - 0.8)
                modifiers.append("Night shift circadian split adjustment (-0.8h)")
            elif metric == "hr":
                adjusted += 2.0
                modifiers.append("Night shift autonomic baseline elevation (+2 bpm)")

        # 2. Environmental context (Heat / Altitude)
        if environment:
            if "Heat" in environment:
                if metric in ("hr", "resting_hr"):
                    adjusted += 4.0
                    modifiers.append("Thermal cardiovascular strain adaptation (+4 bpm)")
            elif "Altitude" in environment:
                if metric == "hr":
                    adjusted += 5.0
                    modifiers.append("High altitude hypoxic compensation (+5 bpm)")
                elif metric == "respiration":
                    adjusted += 2.0
                    modifiers.append("High altitude ventilatory adaptation (+2 br/min)")

        # 3. Tactical Duty Context
        if duty_type:
            if "Rest" in duty_type or "Standby" in duty_type:
                if metric == "activity":
                    adjusted = baseline_median * 0.4
                    modifiers.append("Rest/Standby activity profile")
            elif "Patrol" in duty_type or "Operations" in duty_type:
                if metric == "activity":
                    adjusted = baseline_median * 1.3
                    modifiers.append("Active tactical patrol motion profile")

        return {
            "metric": metric,
            "raw_baseline_median": baseline_median,
            "context_adjusted_expected": round(adjusted, 2),
            "modifiers_applied": modifiers,
            "has_context_adjustment": len(modifiers) > 0,
        }
