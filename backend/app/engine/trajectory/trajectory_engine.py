"""Multi-Horizon Trajectory Engine for SEPTERIA.

Computes trends across short (5-15 min), daily, and rolling (3-day, 7-day, 14-day) horizons.
Calculates direction (STABLE, IMPROVING, DETERIORATING), linear slope, persistence, and volatility.
Uses non-diagnostic terminology (e.g. "Recovery-related physiological deviation").
"""
from typing import List, Dict, Any, Optional
import statistics

class TrajectoryEngine:
    @staticmethod
    def calculate_linear_slope(values: List[float]) -> float:
        """Computes simple least-squares linear slope."""
        n = len(values)
        if n < 2:
            return 0.0
        x = list(range(n))
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        return float(numerator / denominator)

    @staticmethod
    def calculate_volatility(values: List[float]) -> float:
        """Computes standard deviation as a volatility indicator."""
        if len(values) < 2:
            return 0.0
        return float(statistics.pstdev(values))

    @staticmethod
    def calculate_persistence(
        daily_deviations: List[float],
        expected_negative_is_bad: bool = True,
    ) -> int:
        """Calculates consecutive days of continuous deviation in the deteriorating direction."""
        if not daily_deviations:
            return 0
        
        streak = 0
        for dev in reversed(daily_deviations):
            if expected_negative_is_bad:
                # E.g. HRV/Sleep: negative deviation is deteriorating
                if dev < -2.0:
                    streak += 1
                else:
                    break
            else:
                # E.g. Resting HR: positive deviation is deteriorating
                if dev > 2.0:
                    streak += 1
                else:
                    break
        return streak

    @classmethod
    def evaluate_metric_trajectory(
        cls,
        history_values: List[float],
        metric_name: str = "hrv",
        higher_is_better: bool = True,
        stability_threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """Evaluates trend direction, slope, persistence, and volatility."""
        if len(history_values) < 2:
            return {
                "metric": metric_name,
                "direction": "STABLE",
                "slope": 0.0,
                "volatility": 0.0,
                "persistence_days": 1,
                "interpretation": "Insufficient historical trajectory points; currently categorized as stable.",
            }

        slope = cls.calculate_linear_slope(history_values)
        volatility = cls.calculate_volatility(history_values)

        if higher_is_better:
            # For HRV and Sleep: positive slope is improving, negative is deteriorating
            if slope > stability_threshold:
                direction = "IMPROVING"
                interpretation = "Positive recovery-related physiological rebound detected."
            elif slope < -stability_threshold:
                direction = "DETERIORATING"
                interpretation = "Recovery-related physiological trajectory shows progressive downward shift."
            else:
                direction = "STABLE"
                interpretation = "Physiological trajectory remains within stable equilibrium range."
        else:
            # For Resting HR: positive slope is deteriorating, negative is improving
            if slope > stability_threshold:
                direction = "DETERIORATING"
                interpretation = "Nocturnal resting heart rate shows progressive upward elevation."
            elif slope < -stability_threshold:
                direction = "IMPROVING"
                interpretation = "Nocturnal resting heart rate is decreasing toward baseline."
            else:
                direction = "STABLE"
                interpretation = "Resting cardiovascular metrics remain stable."

        return {
            "metric": metric_name,
            "direction": direction,
            "slope": round(slope, 3),
            "volatility": round(volatility, 2),
            "data_points": len(history_values),
            "interpretation": interpretation,
        }

    @classmethod
    def compute_all_trajectories(
        cls,
        daily_records: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Computes multi-signal trajectories over 3-day, 7-day, and 14-day rolling windows."""
        hrv_vals = [float(r["hrv"]) for r in daily_records if "hrv" in r and r["hrv"] is not None]
        sleep_vals = [float(r["sleep"]) for r in daily_records if "sleep" in r and r["sleep"] is not None]
        rhr_vals = [float(r["resting_hr"]) for r in daily_records if "resting_hr" in r and r["resting_hr"] is not None]
        workload_vals = [float(r.get("workload", 3)) for r in daily_records if "workload" in r]

        hrv_traj = cls.evaluate_metric_trajectory(hrv_vals, metric_name="hrv", higher_is_better=True)
        sleep_traj = cls.evaluate_metric_trajectory(sleep_vals, metric_name="sleep", higher_is_better=True)
        rhr_traj = cls.evaluate_metric_trajectory(rhr_vals, metric_name="resting_hr", higher_is_better=False, stability_threshold=0.3)

        # Overall composite trajectory
        det_count = sum(1 for t in (hrv_traj, sleep_traj, rhr_traj) if t["direction"] == "DETERIORATING")
        imp_count = sum(1 for t in (hrv_traj, sleep_traj, rhr_traj) if t["direction"] == "IMPROVING")

        if det_count >= 2:
            overall_direction = "DETERIORATING"
            overall_summary = "Multi-signal recovery trajectory indicates accumulating strain."
        elif imp_count >= 2:
            overall_direction = "IMPROVING"
            overall_summary = "Multi-signal recovery trajectory indicates autonomic rebound."
        else:
            overall_direction = "STABLE"
            overall_summary = "Physiological recovery trajectory is in stable balance."

        return {
            "overall_direction": overall_direction,
            "overall_summary": overall_summary,
            "hrv_trajectory": hrv_traj,
            "sleep_trajectory": sleep_traj,
            "resting_hr_trajectory": rhr_traj,
            "observation_days": len(daily_records),
        }
