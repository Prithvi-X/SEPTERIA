from typing import Dict, Any, List, Optional, Tuple

class ValidationResult:
    def __init__(self, is_valid: bool, record: Dict[str, Any], errors: List[str], warnings: List[str]):
        self.is_valid = is_valid
        self.record = record
        self.errors = errors
        self.warnings = warnings

class PhysiologicalValidator:
    """
    Validates physiological telemetry against human biological boundaries and temporal continuity rules.
    Prevents corrupt or sensor-glitch records from poisoning the evidence pipeline.
    """

    # Human Biological Feasibility Ranges
    HR_MIN = 35.0
    HR_MAX = 220.0
    HRV_MIN = 3.0
    HRV_MAX = 300.0
    SLEEP_MIN = 0.0
    SLEEP_MAX = 20.0
    TEMP_MIN = 30.0
    TEMP_MAX = 44.0
    ACTIVITY_MIN = 0.0

    @classmethod
    def validate(cls, record: Dict[str, Any], previous_record: Optional[Dict[str, Any]] = None) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []
        validated = dict(record)

        # 1. Heart Rate Validation
        hr = record.get("hr")
        if hr is not None:
            if hr < cls.HR_MIN or hr > cls.HR_MAX:
                errors.append(f"Heart Rate {hr} bpm is biologically impossible (range {cls.HR_MIN}-{cls.HR_MAX}).")
            elif previous_record and previous_record.get("hr") is not None:
                # Sudden non-exertional jump check
                prev_hr = previous_record["hr"]
                act = record.get("activity", 0.0)
                if abs(hr - prev_hr) > 50.0 and act < 1000.0:
                    warnings.append(f"Sudden HR jump from {prev_hr} to {hr} bpm without detected physical motion (glitch risk).")
        else:
            warnings.append("Heart Rate observation is missing.")

        # 2. HRV (rMSSD) Validation
        hrv = record.get("hrv")
        if hrv is not None:
            if hrv < cls.HRV_MIN or hrv > cls.HRV_MAX:
                errors.append(f"HRV {hrv} ms is outside plausible physiological boundaries (range {cls.HRV_MIN}-{cls.HRV_MAX}).")
        else:
            warnings.append("HRV observation is missing.")

        # 3. Sleep Duration Validation
        sleep = record.get("sleep")
        if sleep is not None:
            if sleep < cls.SLEEP_MIN or sleep > cls.SLEEP_MAX:
                errors.append(f"Sleep duration {sleep} hrs is outside valid range (0-20 hrs).")

        # 4. Temperature Validation
        temp = record.get("temperature")
        if temp is not None:
            if temp < cls.TEMP_MIN or temp > cls.TEMP_MAX:
                errors.append(f"Body/Skin temperature {temp} °C is outside physiological range ({cls.TEMP_MIN}-{cls.TEMP_MAX}).")

        # 5. Activity Validation
        activity = record.get("activity")
        if activity is not None and activity < cls.ACTIVITY_MIN:
            errors.append(f"Activity measure {activity} cannot be negative.")

        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, record=validated, errors=errors, warnings=warnings)
