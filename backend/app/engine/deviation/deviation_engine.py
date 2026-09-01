"""Personal Deviation Engine for SEPTERIA.

Computes absolute, relative percentage, and robust standardized deviations
from an individual's personal baseline.
Outputs state evidence, NOT clinical diagnoses.
"""
from typing import Dict, Any, Optional
from ..baseline.robust_stats import RobustStats

class PersonalDeviationEngine:
    @staticmethod
    def calculate_metric_deviation(
        observed_value: Optional[float],
        baseline_median: float,
        baseline_mad: float,
        metric_name: str = "metric",
    ) -> Dict[str, Any]:
        """Computes deviation parameters for a single metric."""
        if observed_value is None:
            return {
                "metric": metric_name,
                "observed": None,
                "baseline_median": baseline_median,
                "baseline_mad": baseline_mad,
                "absolute_deviation": None,
                "relative_deviation_pct": None,
                "robust_z_score": None,
                "is_missing": True,
            }

        obs = float(observed_value)
        abs_dev = round(obs - baseline_median, 2)
        rel_pct = round((abs_dev / max(baseline_median, 0.1)) * 100.0, 1)
        z_robust = round(RobustStats.robust_z_score(obs, baseline_median, baseline_mad), 2)

        return {
            "metric": metric_name,
            "observed": obs,
            "baseline_median": baseline_median,
            "baseline_mad": baseline_mad,
            "absolute_deviation": abs_dev,
            "relative_deviation_pct": rel_pct,
            "robust_z_score": z_robust,
            "is_missing": False,
        }

    @classmethod
    def compute_all_deviations(
        cls,
        current_observation: Dict[str, Any],
        baselines: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Computes multi-signal deviation vector against personal baseline."""
        deviations = {}

        # 1. HRV Deviation
        hrv_base = baselines.get("hrv_rmssd", baselines.get("hrv", {"median": 52.0, "mad": 8.0}))
        hrv_obs = current_observation.get("hrv") or current_observation.get("hrv_rmssd")
        deviations["hrv"] = cls.calculate_metric_deviation(
            observed_value=hrv_obs,
            baseline_median=hrv_base["median"],
            baseline_mad=hrv_base["mad"],
            metric_name="hrv_rmssd",
        )

        # 2. Resting HR Deviation
        rhr_base = baselines.get("resting_hr", {"median": 62.0, "mad": 4.0})
        rhr_obs = current_observation.get("resting_hr") or current_observation.get("hr")
        deviations["resting_hr"] = cls.calculate_metric_deviation(
            observed_value=rhr_obs,
            baseline_median=rhr_base["median"],
            baseline_mad=rhr_base["mad"],
            metric_name="resting_hr",
        )

        # 3. Sleep Deficit & Deviation
        sleep_base = baselines.get("sleep_hours", baselines.get("sleep", {"median": 7.0, "mad": 0.8}))
        sleep_obs = current_observation.get("sleep") or current_observation.get("sleep_hours")
        sleep_dev = cls.calculate_metric_deviation(
            observed_value=sleep_obs,
            baseline_median=sleep_base["median"],
            baseline_mad=sleep_base["mad"],
            metric_name="sleep_hours",
        )
        sleep_deficit = 0.0
        if sleep_obs is not None and sleep_obs < sleep_base["median"]:
            sleep_deficit = round(sleep_base["median"] - sleep_obs, 2)
        sleep_dev["sleep_deficit_hours"] = sleep_deficit
        deviations["sleep"] = sleep_dev

        # 4. Activity Deviation
        act_base = baselines.get("activity", {"median": 7000.0, "mad": 1500.0})
        act_obs = current_observation.get("activity")
        deviations["activity"] = cls.calculate_metric_deviation(
            observed_value=act_obs,
            baseline_median=act_base["median"],
            baseline_mad=act_base["mad"],
            metric_name="activity",
        )

        return deviations
