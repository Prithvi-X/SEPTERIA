"""Personal Baseline Engine for SEPTERIA.

Coordinates robust statistical baseline calculation, cold-start handling,
conservative adaptation, and quality stamping for an individual personnel member.
"""
from typing import List, Dict, Any, Optional
from .robust_stats import RobustStats
from .cold_start import ColdStartEngine, DEFAULT_MIN_OBSERVATIONS_THRESHOLD
from .adaptation import ConservativeAdaptationEngine
from .context_adjuster import ContextAdjuster

class PersonalBaselineEngine:
    def __init__(self, min_observations: int = DEFAULT_MIN_OBSERVATIONS_THRESHOLD):
        self.cold_start_engine = ColdStartEngine(min_observations=min_observations)
        self.adaptation_engine = ConservativeAdaptationEngine()

    def compute_metric_baseline(
        self,
        metric: str,
        records: List[Dict[str, Any]],
        existing_baseline: Optional[Dict[str, Any]] = None,
        force: Optional[str] = None,
        role: Optional[str] = None,
        zone: Optional[str] = None,
        recent_daily_trends: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Calculates or updates personal baseline for a specific metric."""
        valid_values = self.adaptation_engine.filter_quality_observations(records, metric)

        if self.cold_start_engine.is_cold_start(len(valid_values)):
            # If historical records are insufficient, use contextual cohort prior
            return self.cold_start_engine.get_cohort_prior(
                metric=metric,
                force=force,
                role=role,
                zone=zone,
            )

        if existing_baseline:
            return self.adaptation_engine.update_baseline_conservative(
                current_baseline=existing_baseline,
                new_observations=valid_values,
                metric=metric,
                recent_daily_trends=recent_daily_trends,
            )

        # First-time calculation from sufficient personal observations
        stats = RobustStats.compute_robust_summary(valid_values)
        return {
            "median": stats["median"],
            "mad": stats["mad"],
            "p10": stats["p10"],
            "p90": stats["p90"],
            "mean": stats["mean"],
            "std": stats["std"],
            "observation_count": len(valid_values),
            "coverage_pct": min(100.0, round(len(valid_values) / 14.0 * 100, 1)),
            "quality_rating": "GOOD" if len(valid_values) >= 10 else "FAIR",
            "is_cohort_prior": False,
            "adaptation_note": "Personal baseline initialized from valid observations.",
        }

    def compute_all_baselines(
        self,
        records: List[Dict[str, Any]],
        existing_baselines: Optional[Dict[str, Dict[str, Any]]] = None,
        force: Optional[str] = None,
        role: Optional[str] = None,
        zone: Optional[str] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """Computes baselines for all core physiological metrics."""
        metrics = ["hr", "hrv_rmssd", "resting_hr", "sleep_hours", "activity"]
        baselines = {}
        existing = existing_baselines or {}

        for m in metrics:
            metric_key = "hrv" if m == "hrv_rmssd" else ("sleep" if m == "sleep_hours" else m)
            # Filter daily trend if available
            daily_vals = [float(r[metric_key]) for r in records if metric_key in r and r[metric_key] is not None]
            
            baselines[m] = self.compute_metric_baseline(
                metric=metric_key,
                records=records,
                existing_baseline=existing.get(m),
                force=force,
                role=role,
                zone=zone,
                recent_daily_trends=daily_vals,
            )
        return baselines
