from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

class SyntheticScenarioGenerator:
    """
    Generates reproducible synthetic physiological & contextual scenarios for testing and demonstration.
    All generated outputs are explicitly labeled as is_synthetic = True.
    """

    @classmethod
    def generate_scenario(
        cls,
        scenario_code: str,
        personnel_id: str = "P-1047",
        days: int = 7,
        end_time: datetime = None,
    ) -> List[Dict[str, Any]]:
        now = end_time or datetime.utcnow()
        records: List[Dict[str, Any]] = []

        code = scenario_code.upper().strip()

        # SCENARIO A: Normal Recovery
        if code in ["A", "NORMAL", "NORMAL_RECOVERY"]:
            for d in range(days, 0, -1):
                t = now - timedelta(days=d, hours=2)
                records.append({
                    "personnel_id": personnel_id,
                    "timestamp": t,
                    "hr": float(70 + random.randint(-3, 4)),
                    "hrv": float(56 + random.randint(-4, 6)),
                    "resting_hr": float(60 + random.randint(-2, 3)),
                    "sleep": float(7.2 + random.uniform(-0.4, 0.5)),
                    "activity": float(6200 + random.randint(-500, 1000)),
                    "respiration": 15.5,
                    "temperature": 36.6,
                    "signal_quality": 0.98,
                    "is_synthetic": True,
                    "source": "synthetic_generator",
                    "scenario": "NORMAL_RECOVERY",
                })

        # SCENARIO B: Physical Exertion
        elif code in ["B", "EXERTION", "PHYSICAL_EXERTION"]:
            for d in range(days, 0, -1):
                t = now - timedelta(days=d, hours=2)
                is_exertion_day = (d <= 2)
                records.append({
                    "personnel_id": personnel_id,
                    "timestamp": t,
                    "hr": float(145.0 if is_exertion_day else 72.0),
                    "hrv": float(38.0 if is_exertion_day else 54.0),
                    "resting_hr": float(64.0),
                    "sleep": float(6.8),
                    "activity": float(14500.0 if is_exertion_day else 6500.0),
                    "respiration": float(24.0 if is_exertion_day else 16.0),
                    "temperature": float(37.4 if is_exertion_day else 36.6),
                    "signal_quality": 0.92,
                    "is_synthetic": True,
                    "source": "synthetic_generator",
                    "scenario": "PHYSICAL_EXERTION",
                })

        # SCENARIO C: High Heat + Physical Exertion
        elif code in ["C", "HEAT", "HEAT_EXERTION"]:
            for d in range(days, 0, -1):
                t = now - timedelta(days=d, hours=2)
                records.append({
                    "personnel_id": personnel_id,
                    "timestamp": t,
                    "hr": float(138.0 + random.randint(-4, 8)),
                    "hrv": float(36.0 + random.randint(-4, 4)),
                    "resting_hr": float(72.0 + random.randint(-2, 4)),
                    "sleep": float(5.8 + random.uniform(-0.5, 0.5)),
                    "activity": float(12000.0 + random.randint(-1000, 2000)),
                    "respiration": 22.0,
                    "temperature": float(37.8 + random.uniform(-0.2, 0.4)),
                    "signal_quality": 0.90,
                    "is_synthetic": True,
                    "source": "synthetic_generator",
                    "scenario": "HEAT_EXERTION",
                })

        # SCENARIO D: Poor Sleep + Increasing Workload (Recovery Decline)
        elif code in ["D", "RECOVERY_DECLINE", "WORKLOAD_STRAIN"]:
            hrv_start = 58.0
            rhr_start = 60.0
            for d in range(days, 0, -1):
                step = days - d
                t = now - timedelta(days=d, hours=2)
                records.append({
                    "personnel_id": personnel_id,
                    "timestamp": t,
                    "hr": float(76.0 + (step * 2.5)),
                    "hrv": max(22.0, float(hrv_start - (step * 4.0))),
                    "resting_hr": float(rhr_start + (step * 2.5)),
                    "sleep": max(3.5, float(6.5 - (step * 0.4))),
                    "activity": float(7500.0 + (step * 800)),
                    "respiration": 17.5,
                    "temperature": 36.7,
                    "signal_quality": 0.95,
                    "is_synthetic": True,
                    "source": "synthetic_generator",
                    "scenario": "RECOVERY_DECLINE",
                })

        # SCENARIO E: Sensor Dropout / 20-Minute Missing HRV Segment
        elif code in ["E", "MISSING_DATA", "SENSOR_DROPOUT"]:
            # Generate 60 minutes of minute-by-minute records, with minutes 20..40 omitted (20-min gap)
            base_t = now - timedelta(minutes=60)
            for m in range(60):
                # Inject 20-minute gap: skip minutes 20 to 39
                if 20 <= m < 40:
                    continue
                t = base_t + timedelta(minutes=m)
                records.append({
                    "personnel_id": personnel_id,
                    "timestamp": t,
                    "hr": float(72 + random.randint(-3, 3)),
                    "hrv": float(54 + random.randint(-4, 4)),
                    "resting_hr": 62.0,
                    "sleep": 7.0,
                    "activity": float(500 + random.randint(-50, 100)),
                    "respiration": 16.0,
                    "temperature": 36.6,
                    "signal_quality": 0.96,
                    "is_synthetic": True,
                    "source": "synthetic_generator",
                    "scenario": "SENSOR_DROPOUT_20MIN",
                })

        # SCENARIO F: Post-Leave Transition Deterioration
        elif code in ["F", "POST_LEAVE_DETERIORATION"]:
            for d in range(days, 0, -1):
                t = now - timedelta(days=d, hours=2)
                records.append({
                    "personnel_id": personnel_id,
                    "timestamp": t,
                    "hr": float(78.0 + random.randint(-2, 4)),
                    "hrv": float(42.0 + random.randint(-3, 3)),
                    "resting_hr": float(68.0),
                    "sleep": float(5.2 + random.uniform(-0.5, 0.5)),
                    "activity": float(8200.0),
                    "respiration": 17.0,
                    "temperature": 36.6,
                    "signal_quality": 0.94,
                    "is_synthetic": True,
                    "source": "synthetic_generator",
                    "scenario": "POST_LEAVE_DETERIORATION",
                })

        # SCENARIO G: Contradictory Signals
        elif code in ["G", "CONTRADICTORY", "CONTRADICTORY_SIGNALS"]:
            for d in range(days, 0, -1):
                t = now - timedelta(days=d, hours=2)
                records.append({
                    "personnel_id": personnel_id,
                    "timestamp": t,
                    "hr": float(106.0), # Elevated HR
                    "hrv": float(34.0),  # Depressed HRV
                    "resting_hr": float(76.0),
                    "sleep": float(7.5), # Normal sleep reported
                    "activity": float(1800.0), # Low motion
                    "respiration": 16.0,
                    "temperature": 36.6,
                    "signal_quality": 0.95,
                    "is_synthetic": True,
                    "source": "synthetic_generator",
                    "scenario": "CONTRADICTORY_SIGNALS",
                })

        else:
            # Default to Normal Recovery
            return cls.generate_scenario("A", personnel_id=personnel_id, days=days, end_time=now)

        return records
