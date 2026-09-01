"""Robust Non-Gaussian Statistical Module for SEPTERIA Baseline Calculations.

Provides median, Median Absolute Deviation (MAD), percentiles, and robust modified Z-scores.
Zero reliance on Gaussian distribution assumptions.
"""
from typing import List, Dict, Any, Tuple, Optional
import statistics

class RobustStats:
    @staticmethod
    def calculate_median(values: List[float]) -> float:
        if not values:
            return 0.0
        return float(statistics.median(values))

    @staticmethod
    def calculate_mad(values: List[float], median: Optional[float] = None) -> float:
        """Computes Median Absolute Deviation (MAD) = median(|x_i - median(x)|)."""
        if not values:
            return 1.0
        med = median if median is not None else statistics.median(values)
        deviations = [abs(x - med) for x in values]
        mad = float(statistics.median(deviations))
        # Prevent division by zero with small epsilon floor
        return max(mad, 0.5)

    @staticmethod
    def calculate_percentiles(values: List[float], p10: float = 10, p90: float = 90) -> Tuple[float, float]:
        if not values:
            return (0.0, 0.0)
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        if n == 1:
            return (float(sorted_vals[0]), float(sorted_vals[0]))
        
        idx_10 = int(round((p10 / 100.0) * (n - 1)))
        idx_90 = int(round((p90 / 100.0) * (n - 1)))
        return (float(sorted_vals[idx_10]), float(sorted_vals[idx_90]))

    @staticmethod
    def robust_z_score(value: float, median: float, mad: float) -> float:
        """Modified robust Z-score: 0.6745 * (x - median) / MAD.
        
        0.6745 is the consistency constant for the normal distribution equivalent scale.
        """
        effective_mad = max(mad, 0.5)
        return float(0.6745 * (value - median) / effective_mad)

    @classmethod
    def compute_robust_summary(cls, values: List[float]) -> Dict[str, Any]:
        if not values:
            return {
                "median": 0.0,
                "mad": 1.0,
                "p10": 0.0,
                "p90": 0.0,
                "mean": 0.0,
                "std": 0.0,
                "count": 0,
            }
        med = cls.calculate_median(values)
        mad = cls.calculate_mad(values, med)
        p10, p90 = cls.calculate_percentiles(values)
        mean_val = float(statistics.mean(values))
        std_val = float(statistics.pstdev(values)) if len(values) > 1 else 0.0
        
        return {
            "median": round(med, 2),
            "mad": round(mad, 2),
            "p10": round(p10, 2),
            "p90": round(p90, 2),
            "mean": round(mean_val, 2),
            "std": round(std_val, 2),
            "count": len(values),
        }
