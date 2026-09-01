"""Recovery Debt / Accumulated Strain Prototype Engine for SEPTERIA.

Computes an explainable composite indicator (0 - 100) summarizing multi-day recovery strain.

IMPORTANT SCIENTIFIC DISCLAIMER (User Refinement 1):
The composite weights used in this module are PROVISIONAL PROTOTYPE HEURISTICS.
They are NOT scientifically or clinically validated diagnostic weights.
They serve as a transparent analytical feature layer that requires operational calibration.
"""
from typing import Dict, Any, List, Optional

# Configurable prototype heuristic weights (Default: 30 / 25 / 20 / 15 / 10)
DEFAULT_RECOVERY_DEBT_WEIGHTS = {
    "sleep_deficit_weight": 30.0,
    "hrv_suppression_weight": 25.0,
    "rhr_elevation_weight": 20.0,
    "consecutive_workload_weight": 15.0,
    "post_leave_friction_weight": 10.0,
}

class RecoveryDebtEngine:
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or DEFAULT_RECOVERY_DEBT_WEIGHTS

    def calculate_recovery_debt(
        self,
        sleep_deficit_hours: float = 0.0,
        hrv_suppression_pct: float = 0.0,
        rhr_elevation_bpm: float = 0.0,
        consecutive_high_workload_days: int = 0,
        is_post_leave_transition: bool = False,
        post_leave_day: int = 0,
    ) -> Dict[str, Any]:
        """Calculates 0-100 composite recovery burden score with transparent factor breakdown."""
        w_sleep = self.weights.get("sleep_deficit_weight", 30.0)
        w_hrv = self.weights.get("hrv_suppression_weight", 25.0)
        w_rhr = self.weights.get("rhr_elevation_weight", 20.0)
        w_workload = self.weights.get("consecutive_workload_weight", 15.0)
        w_leave = self.weights.get("post_leave_friction_weight", 10.0)

        # 1. Sleep Deficit Subscore (Cap at 3 hours deficit -> 100% of subscore)
        sleep_ratio = min(1.0, max(0.0, sleep_deficit_hours / 3.0))
        sleep_contrib = sleep_ratio * w_sleep

        # 2. HRV Suppression Subscore (Cap at 35% suppression -> 100% of subscore)
        hrv_ratio = min(1.0, max(0.0, hrv_suppression_pct / 35.0))
        hrv_contrib = hrv_ratio * w_hrv

        # 3. Resting HR Elevation Subscore (Cap at 12 bpm elevation -> 100% of subscore)
        rhr_ratio = min(1.0, max(0.0, rhr_elevation_bpm / 12.0))
        rhr_contrib = rhr_ratio * w_rhr

        # 4. Consecutive High Workload Days (Cap at 5 consecutive days -> 100% of subscore)
        workload_ratio = min(1.0, max(0.0, consecutive_high_workload_days / 5.0))
        workload_contrib = workload_ratio * w_workload

        # 5. Post-Leave Transition Friction (Highest in early days 1-5 / 14)
        leave_contrib = 0.0
        if is_post_leave_transition and post_leave_day <= 14:
            leave_factor = max(0.2, (14 - post_leave_day) / 14.0)
            leave_contrib = leave_factor * w_leave

        # Total Composite Score
        total_score = min(100.0, max(0.0, sleep_contrib + hrv_contrib + rhr_contrib + workload_contrib + leave_contrib))

        # Human-readable breakdown
        factors = []
        if sleep_deficit_hours > 0.5:
            factors.append(f"Sleep deficit: {sleep_deficit_hours:.1f}h below baseline (+{sleep_contrib:.1f} pts)")
        if hrv_suppression_pct > 10.0:
            factors.append(f"HRV suppression: {hrv_suppression_pct:.1f}% below baseline (+{hrv_contrib:.1f} pts)")
        if rhr_elevation_bpm > 3.0:
            factors.append(f"Resting HR elevation: +{rhr_elevation_bpm:.1f} bpm (+{rhr_contrib:.1f} pts)")
        if consecutive_high_workload_days >= 2:
            factors.append(f"{consecutive_high_workload_days} consecutive high-workload shifts (+{workload_contrib:.1f} pts)")
        if is_post_leave_transition:
            factors.append(f"Post-leave transition (Day {post_leave_day}/14) (+{leave_contrib:.1f} pts)")

        if not factors:
            factors.append("Recovery indicators in stable physiological balance.")

        return {
            "recovery_burden_score": round(total_score, 1),
            "contributing_factors": factors,
            "subscores": {
                "sleep_contribution": round(sleep_contrib, 1),
                "hrv_contribution": round(hrv_contrib, 1),
                "rhr_contribution": round(rhr_contrib, 1),
                "workload_contribution": round(workload_contrib, 1),
                "post_leave_contribution": round(leave_contrib, 1),
            },
            "weights_used": self.weights,
            "disclaimer": "Provisional prototype indicator; not a validated clinical instrument.",
        }
