from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from shared.constants.evidence import GapType, EvidenceStatus, SQIStatus

class MissingDataHandler:
    """
    Detects sensor dropouts, tracks missing intervals, calculates multimodal data completeness,
    and applies conservative deterministic interpolation strictly tagged as INFERRED.
    """

    SHORT_GAP_MAX_MINUTES = 15.0
    LONG_GAP_MAX_MINUTES = 60.0

    @classmethod
    def classify_gap(cls, duration_minutes: float) -> str:
        if duration_minutes <= cls.SHORT_GAP_MAX_MINUTES:
            return GapType.SHORT_GAP.value
        elif duration_minutes <= cls.LONG_GAP_MAX_MINUTES:
            return GapType.LONG_GAP.value
        else:
            return GapType.CONTINUOUS_DROPOUT.value

    @classmethod
    def detect_gaps(
        cls,
        personnel_id: str,
        signal_name: str,
        records: List[Dict[str, Any]],
        expected_interval_minutes: float = 1.0,
    ) -> List[Dict[str, Any]]:
        """
        Scans sorted timestamped records and returns detected gap intervals.
        """
        if len(records) < 2:
            return []

        sorted_recs = sorted(records, key=lambda x: x["timestamp"])
        gaps: List[Dict[str, Any]] = []

        for i in range(len(sorted_recs) - 1):
            t_curr = sorted_recs[i]["timestamp"]
            t_next = sorted_recs[i + 1]["timestamp"]
            delta = (t_next - t_curr).total_seconds() / 60.0

            # If gap exceeds 2x expected interval (e.g. > 2 mins for 1-min sampling)
            if delta > (expected_interval_minutes * 2.0):
                gap_duration = delta - expected_interval_minutes
                gap_type = cls.classify_gap(gap_duration)
                gaps.append({
                    "personnel_id": personnel_id,
                    "signal_name": signal_name,
                    "start_time": t_curr + timedelta(minutes=expected_interval_minutes),
                    "end_time": t_next,
                    "duration_minutes": round(gap_duration, 1),
                    "gap_type": gap_type,
                    "reconstructed": False,
                    "reconstruction_method": None,
                })

        return gaps

    @classmethod
    def calculate_completeness(
        cls,
        total_expected_intervals: int,
        observed_intervals: int,
    ) -> float:
        """
        Calculates percentage completeness (0.0% to 100.0%).
        """
        if total_expected_intervals <= 0:
            return 100.0
        pct = (observed_intervals / total_expected_intervals) * 100.0
        return round(max(0.0, min(100.0, pct)), 1)

    @classmethod
    def interpolate_short_gaps(
        cls,
        records: List[Dict[str, Any]],
        expected_interval_minutes: float = 1.0,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Conservatively interpolates only SHORT gaps (< 15 mins) when visualization continuity is needed.
        Every interpolated record is strictly tagged with evidence_status = INFERRED.
        Returns (augmented_records, reconstructed_gaps).
        """
        if len(records) < 2:
            return records, []

        sorted_recs = sorted(records, key=lambda x: x["timestamp"])
        augmented: List[Dict[str, Any]] = []
        reconstructed_gaps: List[Dict[str, Any]] = []

        for i in range(len(sorted_recs) - 1):
            r1 = sorted_recs[i]
            r2 = sorted_recs[i + 1]
            augmented.append(r1)

            t1 = r1["timestamp"]
            t2 = r2["timestamp"]
            diff_min = (t2 - t1).total_seconds() / 60.0

            # Conservative Rule: ONLY interpolate short gaps <= 15 minutes
            if expected_interval_minutes < diff_min <= cls.SHORT_GAP_MAX_MINUTES:
                steps = int(diff_min / expected_interval_minutes)
                gap_info = {
                    "personnel_id": r1.get("personnel_id", "UNKNOWN"),
                    "signal_name": "multimodal_physiology",
                    "start_time": t1 + timedelta(minutes=expected_interval_minutes),
                    "end_time": t2,
                    "duration_minutes": round(diff_min, 1),
                    "gap_type": GapType.SHORT_GAP.value,
                    "reconstructed": True,
                    "reconstruction_method": "LINEAR_INTERPOLATION",
                }
                reconstructed_gaps.append(gap_info)

                # Generate intermediate inferred points
                for s in range(1, steps):
                    fraction = s / float(steps)
                    t_interp = t1 + timedelta(minutes=s * expected_interval_minutes)
                    hr_interp = r1["hr"] + fraction * (r2["hr"] - r1["hr"]) if r1.get("hr") and r2.get("hr") else r1.get("hr")
                    hrv_interp = r1["hrv"] + fraction * (r2["hrv"] - r1["hrv"]) if r1.get("hrv") and r2.get("hrv") else r1.get("hrv")
                    act_interp = r1["activity"] + fraction * (r2["activity"] - r1["activity"]) if r1.get("activity") and r2.get("activity") else 0.0

                    inferred_rec = dict(r1)
                    inferred_rec["id"] = f"inferred-{t_interp.strftime('%Y%m%d%H%M%S')}"
                    inferred_rec["timestamp"] = t_interp
                    inferred_rec["hr"] = round(hr_interp, 1) if hr_interp else None
                    inferred_rec["hrv"] = round(hrv_interp, 1) if hrv_interp else None
                    inferred_rec["activity"] = round(act_interp, 1)
                    inferred_rec["evidence_status"] = EvidenceStatus.INFERRED.value
                    inferred_rec["sqi_status"] = SQIStatus.FAIR.value
                    inferred_rec["signal_quality"] = 0.70
                    inferred_rec["is_reconstructed"] = True
                    augmented.append(inferred_rec)

        augmented.append(sorted_recs[-1])
        return augmented, reconstructed_gaps
