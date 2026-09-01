from typing import Dict, Any, Tuple
from shared.constants.evidence import MotionContext

class MotionContextClassifier:
    """
    Classifies physical activity intensity to provide context for cardiovascular telemetry.
    Ensures physiological elevation during physical movement is recognized as exercise.
    """

    # Thresholds for standardized step / motion intensity indices
    LOW_THRESHOLD = 3000.0
    MODERATE_THRESHOLD = 8000.0
    HIGH_THRESHOLD = 12000.0

    @classmethod
    def classify(cls, activity_index: float, hr: float = None) -> Tuple[str, bool, str]:
        """
        Returns:
        - motion_context: LOW, MODERATE, HIGH, EXERTIONAL
        - is_active_movement: bool
        - description: str
        """
        val = activity_index or 0.0

        if val >= cls.HIGH_THRESHOLD or (val >= cls.MODERATE_THRESHOLD and (hr or 0) >= 130.0):
            return (
                MotionContext.EXERTIONAL.value,
                True,
                "Intense physical exertion / tactical maneuver detected.",
            )
        elif val >= cls.MODERATE_THRESHOLD:
            return (
                MotionContext.HIGH.value,
                True,
                "High physical activity / patrol movement detected.",
            )
        elif val >= cls.LOW_THRESHOLD:
            return (
                MotionContext.MODERATE.value,
                True,
                "Moderate activity / routine movement detected.",
            )
        else:
            return (
                MotionContext.LOW.value,
                False,
                "Low activity / static posture detected.",
            )
