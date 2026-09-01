"""Conservative Baseline Adaptation Module.

Guarantees slow, robust baseline updates.
Critical Safety Rule: Prevents progressive deterioration (e.g. HRV dropping 55 -> 52 -> 49 -> 43 ms)
from being prematurely absorbed as the "new normal" baseline without considering deterioration trajectory.
"""
from typing import List, Dict, Any, Optional
from .robust_stats import RobustStats

class ConservativeAdaptationEngine:
    def __init__(
        self,
        rolling_window_days: int = 14,
        max_daily_drift_pct: float = 5.0, # Max 5% adaptation shift per update cycle
        deterioration_persistence_lock_days: int = 3, # If >=3 consecutive deteriorating days, freeze baseline downward drift
    ):
        self.rolling_window_days = rolling_window_days
        self.max_daily_drift_pct = max_daily_drift_pct
        self.deterioration_persistence_lock_days = deterioration_persistence_lock_days

    def filter_quality_observations(
        self,
        records: List[Dict[str, Any]],
        metric: str,
    ) -> List[float]:
        """Excludes or down-weights POOR/UNCERTAIN quality records."""
        valid_values = []
        for r in records:
            # Exclude POOR signal quality or UNCERTAIN evidence status
            sqi = r.get("sqi_status", "GOOD")
            evidence = r.get("evidence_status", "OBSERVED")
            val = r.get(metric)
            
            if val is not None and sqi not in ("POOR", "MISSING") and evidence != "UNCERTAIN":
                valid_values.append(float(val))
        return valid_values

    def check_persistent_deterioration(
        self,
        daily_averages: List[float],
        metric: str,
    ) -> bool:
        """Detects if a metric has been strictly deteriorating for consecutive days."""
        if len(daily_averages) < self.deterioration_persistence_lock_days:
            return False
        
        # For HRV and Sleep: lower is deteriorating
        # For Resting HR: higher is deteriorating
        recent = daily_averages[-self.deterioration_persistence_lock_days:]
        
        if metric in ("hrv", "hrv_rmssd", "sleep", "sleep_hours"):
            # Check monotonic decrease
            return all(recent[i] < recent[i - 1] for i in range(1, len(recent)))
        elif metric in ("resting_hr", "hr"):
            # Check monotonic increase
            return all(recent[i] > recent[i - 1] for i in range(1, len(recent)))
        return False

    def update_baseline_conservative(
        self,
        current_baseline: Dict[str, Any],
        new_observations: List[float],
        metric: str,
        recent_daily_trends: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Computes updated baseline while strictly gating against premature absorption of strain."""
        if not new_observations:
            return current_baseline

        new_stats = RobustStats.compute_robust_summary(new_observations)
        new_median = new_stats["median"]
        new_mad = new_stats["mad"]

        # If current baseline is a cold-start prior, allow standard initialization
        if current_baseline.get("is_cohort_prior", False) or current_baseline.get("observation_count", 0) == 0:
            return {
                "median": new_median,
                "mad": new_mad,
                "p10": new_stats["p10"],
                "p90": new_stats["p90"],
                "mean": new_stats["mean"],
                "std": new_stats["std"],
                "observation_count": len(new_observations),
                "coverage_pct": min(100.0, round(len(new_observations) / (self.rolling_window_days * 1.0) * 100, 1)),
                "quality_rating": "GOOD" if len(new_observations) >= 7 else "FAIR",
                "is_cohort_prior": False,
                "adaptation_note": "Initial personal baseline computed from valid observations.",
            }

        prev_median = float(current_baseline.get("median", new_median))
        prev_mad = float(current_baseline.get("mad", new_mad))

        # Check for persistent deterioration trajectory
        is_deteriorating = False
        if recent_daily_trends:
            is_deteriorating = self.check_persistent_deterioration(recent_daily_trends, metric)

        if is_deteriorating:
            # FREEZE downward baseline shift for HRV/sleep (or upward for RHR) to preserve the strain comparison signal
            adjusted_median = prev_median
            adaptation_note = "Baseline downward adaptation locked: persistent multi-day recovery deterioration detected."
        else:
            # Apply conservative bounded drift
            max_drift = prev_median * (self.max_daily_drift_pct / 100.0)
            diff = new_median - prev_median
            clamped_diff = max(-max_drift, min(max_drift, diff))
            adjusted_median = round(prev_median + (clamped_diff * 0.3), 2) # Slow 0.3 learning rate
            adaptation_note = "Conservative baseline update applied within drift guardrails."

        total_count = current_baseline.get("observation_count", 0) + len(new_observations)
        
        return {
            "median": adjusted_median,
            "mad": round(max(new_mad, prev_mad * 0.9), 2),
            "p10": new_stats["p10"],
            "p90": new_stats["p90"],
            "mean": new_stats["mean"],
            "std": new_stats["std"],
            "observation_count": total_count,
            "coverage_pct": min(100.0, round(len(new_observations) / float(self.rolling_window_days) * 100, 1)),
            "quality_rating": "GOOD" if total_count >= 14 else "FAIR",
            "is_cohort_prior": False,
            "adaptation_note": adaptation_note,
        }
