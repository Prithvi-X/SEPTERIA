from enum import Enum

class EvidenceStatus(str, Enum):
    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"
    INFERRED = "INFERRED"
    CONTEXTUAL = "CONTEXTUAL"
    UNCERTAIN = "UNCERTAIN"

class SQIStatus(str, Enum):
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"
    MISSING = "MISSING"

class MotionContext(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    EXERTIONAL = "EXERTIONAL"

class GapType(str, Enum):
    SHORT_GAP = "SHORT_GAP"         # < 15 minutes (eligible for conservative interpolation)
    LONG_GAP = "LONG_GAP"           # 15 - 60 minutes
    CONTINUOUS_DROPOUT = "CONTINUOUS_DROPOUT" # > 60 minutes

class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"

class Trajectory(str, Enum):
    STABLE = "STABLE"
    IMPROVING = "IMPROVING"
    DETERIORATING = "DETERIORATING"

class RecommendationPriority(str, Enum):
    ROUTINE = "ROUTINE"
    PRIORITY = "PRIORITY"
    URGENT = "URGENT"

class RecommendationStatus(str, Enum):
    PENDING = "PENDING"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DISMISSED = "DISMISSED"
