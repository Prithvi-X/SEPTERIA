from datetime import datetime
from typing import Dict, Any, Optional

class MultimodalAlignmentEngine:
    """
    Aligns multimodal streams (Physiological, Wellness, Operational, Environmental)
    into a unified temporal evidence frame.
    """

    @staticmethod
    def align(
        physio_record: Dict[str, Any],
        operational_context: Optional[Dict[str, Any]] = None,
        wellness_record: Optional[Dict[str, Any]] = None,
        environmental_record: Optional[Dict[str, Any]] = None,
        post_leave_day_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        ops = operational_context or {}
        well = wellness_record or {}
        env = environmental_record or {}

        aligned: Dict[str, Any] = {
            "timestamp": physio_record.get("timestamp"),
            "personnel_id": physio_record.get("personnel_id"),

            # 1. Physiological Stream (OBSERVED / INFERRED)
            "hr": physio_record.get("hr"),
            "hrv": physio_record.get("hrv"),
            "resting_hr": physio_record.get("resting_hr"),
            "sleep": physio_record.get("sleep"),
            "activity": physio_record.get("activity"),
            "respiration": physio_record.get("respiration"),
            "temperature": physio_record.get("temperature"),
            "sqi_status": physio_record.get("sqi_status", "GOOD"),
            "motion_context": physio_record.get("motion_context", "LOW"),
            "physio_evidence_status": physio_record.get("evidence_status", "OBSERVED"),

            # 2. Authoritative Operational Stream (CONTEXTUAL)
            "operational_zone": ops.get("zone", "Zone 2"),
            "duty_type": ops.get("duty_type", "Standard Duty"),
            "shift": ops.get("shift", "Day"),
            "location": ops.get("location", "Base Station"),
            "is_temporary_deployment": ops.get("temporary", False),
            "post_leave_transition_day": post_leave_day_count,
            "ops_evidence_status": "CONTEXTUAL",

            # 3. Voluntary Wellness Stream (OBSERVED)
            "self_reported_stress": well.get("stress"),
            "self_reported_fatigue": well.get("fatigue"),
            "self_reported_sleep_quality": well.get("sleep_quality"),
            "self_reported_workload": well.get("workload"),
            "wellness_evidence_status": well.get("evidence_status", "OBSERVED") if well else "MISSING",

            # 4. Environmental Stream (CONTEXTUAL)
            "ambient_temperature": env.get("ambient_temp", 28.0),
            "altitude_meters": env.get("altitude", 200.0),
            "relative_humidity": env.get("humidity", 45.0),
            "environment_category": env.get("environment_category", "Standard"),
            "env_evidence_status": "CONTEXTUAL",
        }

        return aligned
