"""Transition-State Engine for SEPTERIA.

Tracks and contextualizes temporal transition states:
- POST_LEAVE_TRANSITION: Day X / 14 (circadian & shift re-adaptation)
- DEPLOYMENT_START / DEPLOYMENT_END: Rotation friction
- POST_INCIDENT_RECOVERY: 24-72h stabilization window
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class TransitionEngine:
    @staticmethod
    def evaluate_leave_transition(
        leave_status: str,
        post_leave_day_count: int,
        total_transition_days: int = 14,
    ) -> Dict[str, Any]:
        """Evaluates post-leave transition state."""
        is_active = leave_status == "POST_LEAVE_TRANSITION" and post_leave_day_count <= total_transition_days
        
        if is_active:
            phase = "EARLY_ADAPTATION" if post_leave_day_count <= 4 else ("MID_ADAPTATION" if post_leave_day_count <= 9 else "STABILIZATION")
            explanation = (
                f"Post-leave reintegration state active (Day {post_leave_day_count}/{total_transition_days}). "
                "Shift changes and sleep schedule adjustments are evaluated in this operational transition context."
            )
        else:
            phase = "NONE"
            explanation = "Standard deployment state (no active post-leave transition)."

        return {
            "transition_type": "POST_LEAVE_TRANSITION",
            "is_transition_active": is_active,
            "current_day": post_leave_day_count if is_active else 0,
            "total_days": total_transition_days,
            "adaptation_phase": phase,
            "explanation": explanation,
        }

    @staticmethod
    def evaluate_deployment_rotation(
        is_temporary: bool,
        remaining_days: float,
        total_deployment_days: float = 7.0,
    ) -> Dict[str, Any]:
        """Evaluates temporary deployment rotation transition."""
        if not is_temporary:
            return {
                "transition_type": "DEPLOYMENT_ROTATION",
                "is_transition_active": False,
                "rotation_phase": "PERMANENT_POSTING",
                "explanation": "Standard permanent unit deployment.",
            }

        elapsed_days = max(0.0, total_deployment_days - remaining_days)
        is_start = elapsed_days <= 2.0
        is_end = remaining_days <= 1.5

        phase = "DEPLOYMENT_START" if is_start else ("DEPLOYMENT_END" if is_end else "MID_DEPLOYMENT")
        return {
            "transition_type": "DEPLOYMENT_ROTATION",
            "is_transition_active": True,
            "rotation_phase": phase,
            "elapsed_days": round(elapsed_days, 1),
            "remaining_days": round(remaining_days, 1),
            "explanation": f"Temporary deployment in {phase.replace('_', ' ').lower()} phase ({remaining_days:.1f} days remaining).",
        }
