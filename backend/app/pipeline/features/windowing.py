from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import statistics

class FeatureWindowEngine:
    """
    Computes time-windowed and rolling aggregated features:
    - Short windows (5-minute, 15-minute)
    - Daily aggregations (mean HR, nocturnal HRV, sleep duration)
    - Rolling trajectories (3-day, 7-day, 14-day rolling baselines)
    All computed aggregations are marked with evidence_status = DERIVED.
    Uses pure Python standard library for zero-dependency portability.
    """

    @staticmethod
    def calculate_short_window(records: List[Dict[str, Any]], window_minutes: int = 5) -> Dict[str, Any]:
        if not records:
            return {}

        hrs = [r["hr"] for r in records if r.get("hr") is not None]
        hrvs = [r["hrv"] for r in records if r.get("hrv") is not None]
        acts = [r["activity"] for r in records if r.get("activity") is not None]

        hr_mean = round(float(statistics.mean(hrs)), 1) if hrs else None
        hr_std = round(float(statistics.pstdev(hrs)), 1) if len(hrs) > 1 else 0.0
        hrv_mean = round(float(statistics.mean(hrvs)), 1) if hrvs else None
        hrv_std = round(float(statistics.pstdev(hrvs)), 1) if len(hrvs) > 1 else 0.0
        act_total = round(float(sum(acts)), 1) if acts else 0.0

        return {
            "window_minutes": window_minutes,
            "record_count": len(records),
            "hr_mean": hr_mean,
            "hr_std": hr_std,
            "hrv_mean": hrv_mean,
            "hrv_std": hrv_std,
            "activity_total": act_total,
            "evidence_status": "DERIVED",
        }

    @staticmethod
    def calculate_rolling_features(daily_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates 3-day, 7-day, and 14-day rolling trajectory summaries.
        """
        if not daily_records:
            return {
                "rolling_3d_hrv": None,
                "rolling_7d_hrv": None,
                "rolling_14d_hrv": None,
                "rolling_7d_sleep": None,
                "evidence_status": "DERIVED",
            }

        sorted_daily = sorted(daily_records, key=lambda x: x["timestamp"])
        hrvs = [r["hrv"] for r in sorted_daily if r.get("hrv") is not None]
        sleeps = [r["sleep"] for r in sorted_daily if r.get("sleep") is not None]

        r3_hrv = round(float(statistics.mean(hrvs[-3:])), 1) if len(hrvs) >= 3 else (round(float(statistics.mean(hrvs)), 1) if hrvs else None)
        r7_hrv = round(float(statistics.mean(hrvs[-7:])), 1) if len(hrvs) >= 7 else (round(float(statistics.mean(hrvs)), 1) if hrvs else None)
        r14_hrv = round(float(statistics.mean(hrvs[-14:])), 1) if len(hrvs) >= 14 else (round(float(statistics.mean(hrvs)), 1) if hrvs else None)
        r7_sleep = round(float(statistics.mean(sleeps[-7:])), 2) if len(sleeps) >= 7 else (round(float(statistics.mean(sleeps)), 2) if sleeps else None)

        return {
            "rolling_3d_hrv": r3_hrv,
            "rolling_7d_hrv": r7_hrv,
            "rolling_14d_hrv": r14_hrv,
            "rolling_7d_sleep": r7_sleep,
            "observation_days": len(sorted_daily),
            "evidence_status": "DERIVED",
        }
