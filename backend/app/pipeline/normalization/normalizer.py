from datetime import datetime, timezone
from typing import Dict, Any, Optional

class DataNormalizer:
    """
    Standardizes internal representation of incoming data streams:
    - UTC Timestamps
    - Unit standardizations (HR: bpm, HRV: rMSSD ms, Sleep: hours, Temp: Celsius, Activity: normalized index)
    - Categorical value alignment
    - Preserves provenance snapshot of original raw payload
    """

    @staticmethod
    def parse_timestamp(ts: Any) -> datetime:
        """
        Parses various timestamp formats (datetime, ISO string, epoch milliseconds/seconds) into UTC datetime.
        """
        if isinstance(ts, datetime):
            if ts.tzinfo is not None:
                return ts.astimezone(timezone.utc).replace(tzinfo=None)
            return ts
        
        if isinstance(ts, (int, float)):
            # Epoch milliseconds vs seconds
            if ts > 1e11:
                return datetime.utcfromtimestamp(ts / 1000.0)
            return datetime.utcfromtimestamp(ts)
        
        if isinstance(ts, str):
            clean_str = ts.replace("Z", "+00:00")
            try:
                dt = datetime.fromisoformat(clean_str)
                if dt.tzinfo is not None:
                    return dt.astimezone(timezone.utc).replace(tzinfo=None)
                return dt
            except Exception:
                pass
        
        return datetime.utcnow()

    @staticmethod
    def normalize_physiological_record(raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes a raw physiological record into standardized numerical and temporal representations.
        """
        # Prepare JSON-serializable snapshot
        snapshot = {}
        for k, v in raw.items():
            if isinstance(v, datetime):
                snapshot[k] = v.isoformat()
            else:
                snapshot[k] = v
        norm: Dict[str, Any] = {}

        # Personnel ID
        norm["personnel_id"] = str(raw.get("personnel_id", "UNKNOWN"))

        # Timestamp
        norm["timestamp"] = DataNormalizer.parse_timestamp(raw.get("timestamp"))

        # Heart Rate (bpm)
        raw_hr = raw.get("hr", raw.get("heart_rate", raw.get("pulse")))
        norm["hr"] = round(float(raw_hr), 1) if raw_hr is not None else None

        # HRV (rMSSD in ms)
        raw_hrv = raw.get("hrv", raw.get("rmssd", raw.get("heart_rate_variability")))
        norm["hrv"] = round(float(raw_hrv), 1) if raw_hrv is not None else None

        # Resting HR (bpm)
        raw_rhr = raw.get("resting_hr", raw.get("rhr", raw.get("resting_heart_rate")))
        if raw_rhr is not None:
            norm["resting_hr"] = round(float(raw_rhr), 1)
        elif norm["hr"] is not None:
            norm["resting_hr"] = round(norm["hr"] * 0.88, 1)
        else:
            norm["resting_hr"] = None

        # Sleep Duration (hours)
        raw_sleep = raw.get("sleep", raw.get("sleep_duration", raw.get("sleep_hours")))
        if raw_sleep is not None:
            val = float(raw_sleep)
            # If provided in minutes (e.g. 420 mins), convert to hours (7.0 hrs)
            if val > 24.0:
                val = val / 60.0
            norm["sleep"] = round(val, 2)
        else:
            norm["sleep"] = None

        # Activity (standardized step / motion index)
        raw_act = raw.get("activity", raw.get("steps", raw.get("active_minutes")))
        norm["activity"] = round(float(raw_act), 1) if raw_act is not None else 0.0

        # Respiration (breaths/min)
        raw_resp = raw.get("respiration", raw.get("breathing_rate"))
        norm["respiration"] = round(float(raw_resp), 1) if raw_resp is not None else 16.0

        # Temperature (Celsius)
        raw_temp = raw.get("temperature", raw.get("temp", raw.get("skin_temp")))
        if raw_temp is not None:
            val = float(raw_temp)
            # If provided in Fahrenheit (e.g. 98.6 F), convert to Celsius (37.0 C)
            if val > 50.0:
                val = (val - 32.0) * 5.0 / 9.0
            norm["temperature"] = round(val, 1)
        else:
            norm["temperature"] = 36.6

        # Provenance & Metadata Preservation
        norm["source"] = raw.get("source", "synthetic_wearable")
        norm["device_type"] = raw.get("device_type", "synthetic_smartband")
        norm["is_synthetic"] = raw.get("is_synthetic", True)
        norm["signal_quality"] = float(raw.get("signal_quality", 1.0))
        norm["raw_data_snapshot"] = snapshot
        norm["processing_version"] = "v1.0"

        return norm
