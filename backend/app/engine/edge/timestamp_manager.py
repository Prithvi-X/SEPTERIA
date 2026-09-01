"""
SEPTERIA Edge Timestamping & Clock Drift Management Engine (Phase 9)

Preserves temporal provenance and handles clock drift between edge wearable/phone and backend:
  - Preserves original device_timestamp, server ingestion_timestamp, and sequence_number.
  - Calculates and tracks clock drift: drift_ms = (server_time - device_time).
  - Flags backwards clock jumps, time anomalies, and excessive drift (> 10 minutes).
  - Converts device timestamps to standardized ISO-8601 UTC.
"""

from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timezone
import dateutil.parser

class EdgeTimestampManager:
    """
    Validates, calibrates, and audits edge sensor timestamps.
    """
    def __init__(self, max_allowed_drift_minutes: float = 10.0):
        self.max_allowed_drift_minutes = max_allowed_drift_minutes
        self.last_observed_device_time: Optional[datetime] = None
        self.last_observed_sequence: Optional[int] = None

    def process_timestamp(
        self,
        device_timestamp_raw: Any,
        sequence_number: int,
        server_ingest_time: Optional[datetime] = None
    ) -> Tuple[datetime, float, List[str]]:
        """
        Parses device timestamp, computes clock drift against server ingestion time,
        and returns: (normalized_utc_datetime, drift_ms, flags)
        """
        server_time = server_ingest_time or datetime.now(timezone.utc)
        flags = []

        # Parse device timestamp
        try:
            if isinstance(device_timestamp_raw, datetime):
                dev_dt = device_timestamp_raw
            elif isinstance(device_timestamp_raw, (int, float)):
                # Unix timestamp in seconds or ms
                if device_timestamp_raw > 1e11: # milliseconds
                    dev_dt = datetime.fromtimestamp(device_timestamp_raw / 1000.0, tz=timezone.utc)
                else:
                    dev_dt = datetime.fromtimestamp(device_timestamp_raw, tz=timezone.utc)
            else:
                dev_dt = dateutil.parser.parse(str(device_timestamp_raw))

            if dev_dt.tzinfo is None:
                dev_dt = dev_dt.replace(tzinfo=timezone.utc)
            else:
                dev_dt = dev_dt.astimezone(timezone.utc)

        except Exception as e:
            flags.append(f"UNPARSEABLE_DEVICE_TIMESTAMP: {str(e)}")
            dev_dt = server_time

        # Compute clock drift (server - device in milliseconds)
        # Note: both must be timezone-aware
        if server_time.tzinfo is None:
            server_time = server_time.replace(tzinfo=timezone.utc)

        drift_seconds = (server_time - dev_dt).total_seconds()
        drift_ms = round(drift_seconds * 1000.0, 1)

        # Drift checks
        if abs(drift_seconds) > (self.max_allowed_drift_minutes * 60.0):
            flags.append(f"EXCESSIVE_CLOCK_DRIFT: {round(drift_seconds / 60.0, 1)} minutes difference from server.")

        if drift_seconds < -60.0:
            flags.append("FUTURE_TIMESTAMP_DETECTED")

        # Monotonicity & sequence order checks
        if self.last_observed_device_time is not None:
            if dev_dt < self.last_observed_device_time:
                flags.append("NON_MONOTONIC_TIMESTAMP: Device clock jumped backwards.")

        if self.last_observed_sequence is not None:
            if sequence_number < self.last_observed_sequence:
                flags.append("OUT_OF_ORDER_SEQUENCE: Received older packet sequence.")

        self.last_observed_device_time = dev_dt
        self.last_observed_sequence = sequence_number

        return dev_dt.replace(tzinfo=None), drift_ms, flags
