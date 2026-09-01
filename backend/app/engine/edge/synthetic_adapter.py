"""
SEPTERIA Synthetic Edge Data Adapter (Phase 9)

Generates deterministic, clinically grounded synthetic telemetry streams for demo mode:
  1. Normal recovery
  2. Physical exertion
  3. Poor sleep + recovery deterioration
  4. Sensor dropout / poor contact
  5. Connectivity loss & later synchronization

Hardware Honesty:
- Explicitly tags all records as is_synthetic = True and device_source = "SYNTHETIC_DEMO".
- Does not claim physical hardware integration.
"""

from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import numpy as np
from backend.app.engine.edge.data_source_adapter import EdgeDataSourceAdapter

class EdgeSyntheticAdapter(EdgeDataSourceAdapter):
    def __init__(self, device_id: str = "SYNTH-DEMO-001"):
        super().__init__(adapter_type="SYNTHETIC_DEMO", device_id=device_id)

    def ingest_raw(self, payload: Union[List[Dict[str, Any]], Dict[str, Any]]) -> List[Dict[str, Any]]:
        if isinstance(payload, dict):
            payload = [payload]
        return [dict(p) for p in payload]

    def validate_packet(self, packet: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        if "hr" in packet and not (30.0 <= packet["hr"] <= 240.0):
            errors.append(f"Heart rate {packet['hr']} out of physiological bounds [30, 240]")
        if "hrv" in packet and not (0.0 <= packet["hrv"] <= 300.0):
            errors.append(f"HRV {packet['hrv']} out of bounds [0, 300]")
        if "temperature" in packet and packet["temperature"] is not None:
            if not (25.0 <= packet["temperature"] <= 45.0):
                errors.append(f"Temperature {packet['temperature']} out of bounds [25, 45]")
        return len(errors) == 0, errors

    def normalize_packet(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(packet)
        normalized["device_id"] = self.device_id
        normalized["device_source"] = self.adapter_type
        normalized["is_synthetic"] = True
        normalized["evidence_status"] = packet.get("evidence_status", "OBSERVED")
        normalized["source_quality"] = float(packet.get("source_quality", 1.0))
        return normalized

    def generate_demo_stream(
        self,
        scenario: str = "NORMAL_RECOVERY",
        num_records: int = 10,
        start_time: Optional[datetime] = None,
        interval_seconds: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Generates realistic time-series telemetry packets for a specified demo scenario.
        """
        start = start_time or (datetime.utcnow() - timedelta(seconds=num_records * interval_seconds))
        records = []

        np.random.seed(42) # Reproducible demo stream

        for i in range(num_records):
            t = start + timedelta(seconds=i * interval_seconds)
            seq = i + 1

            if scenario == "NORMAL_RECOVERY":
                hr = float(68.0 + 3.0 * np.sin(i / 3.0) + np.random.normal(0, 1.5))
                hrv = float(65.0 + 5.0 * np.cos(i / 3.0) + np.random.normal(0, 2.0))
                resting_hr = 62.0
                activity = float(max(0.0, 0.15 + np.random.normal(0, 0.05)))
                temp = float(36.6 + np.random.normal(0, 0.1))
                sleep = 7.8
                motion_context = "LOW"
                sqi = 0.96
                evidence_status = "OBSERVED"

            elif scenario == "PHYSICAL_EXERTION":
                # Elevated kinetic motion and cardiac response
                hr = float(145.0 + 8.0 * np.sin(i / 2.0) + np.random.normal(0, 3.0))
                hrv = float(18.0 + np.random.normal(0, 1.5))
                resting_hr = 64.0
                activity = float(2.8 + np.random.normal(0, 0.3)) # Exertional ACC energy
                temp = float(37.4 + np.random.normal(0, 0.15))
                sleep = 7.0
                motion_context = "EXERTIONAL"
                sqi = 0.82
                evidence_status = "OBSERVED"

            elif scenario == "POOR_SLEEP_RECOVERY_DECLINE":
                # Sleep debt, elevated resting HR, suppressed HRV
                hr = float(88.0 + 4.0 * np.sin(i / 4.0) + np.random.normal(0, 2.0))
                hrv = float(24.0 + np.random.normal(0, 2.0))
                resting_hr = 84.0
                activity = float(0.40 + np.random.normal(0, 0.1))
                temp = float(36.9 + np.random.normal(0, 0.1))
                sleep = 3.8 # Severe sleep deficit
                motion_context = "MODERATE"
                sqi = 0.90
                evidence_status = "OBSERVED"

            elif scenario == "SENSOR_DROPOUT":
                # Intermittent sensor contact degradation
                is_dropout = (i % 3 == 0)
                hr = float(72.0 + np.random.normal(0, 2.0)) if not is_dropout else 0.0
                hrv = float(50.0 + np.random.normal(0, 3.0)) if not is_dropout else 0.0
                resting_hr = 68.0
                activity = 0.2
                temp = float(36.5) if not is_dropout else None
                sleep = 6.5
                motion_context = "LOW"
                sqi = 0.25 if is_dropout else 0.85
                evidence_status = "UNCERTAIN" if is_dropout else "OBSERVED"

            elif scenario == "CONNECTIVITY_LOSS_SYNC":
                # Regular stream representing offline queued records
                hr = float(75.0 + 2.0 * np.sin(i) + np.random.normal(0, 1.0))
                hrv = float(48.0 + np.random.normal(0, 2.0))
                resting_hr = 66.0
                activity = 0.35
                temp = 36.7
                sleep = 6.8
                motion_context = "LOW"
                sqi = 0.94
                evidence_status = "OBSERVED"
            else:
                hr = 70.0
                hrv = 55.0
                resting_hr = 65.0
                activity = 0.2
                temp = 36.6
                sleep = 7.0
                motion_context = "LOW"
                sqi = 1.0
                evidence_status = "OBSERVED"

            rec = {
                "device_id": self.device_id,
                "device_source": "SYNTHETIC_DEMO",
                "device_timestamp": t.isoformat(),
                "sequence_number": seq,
                "hr": round(hr, 1),
                "hrv": round(hrv, 1),
                "resting_hr": round(resting_hr, 1),
                "activity": round(activity, 2),
                "temperature": round(temp, 1) if temp is not None else None,
                "sleep": round(sleep, 1),
                "motion_context": motion_context,
                "source_quality": round(sqi, 2),
                "evidence_status": evidence_status,
                "scenario": scenario,
                "is_synthetic": True
            }
            records.append(self.normalize_packet(rec))

        return records
