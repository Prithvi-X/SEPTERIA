from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class BaselineMetricResponse(BaseModel):
    metric: str
    median: float
    mad: float
    p10: Optional[float] = None
    p90: Optional[float] = None
    mean: Optional[float] = None
    std: Optional[float] = None
    observation_count: int
    coverage_pct: float
    quality_rating: str # GOOD, FAIR, LOW
    is_cohort_prior: bool = False
    context_modifiers: Optional[Dict[str, Any]] = None

class PersonalBaselineResponse(BaseModel):
    personnel_id: str
    baselines: Dict[str, BaselineMetricResponse]
    last_updated: datetime
    data_classification: str = "SYNTHETIC_DEMO_DATA"

class MetricDeviationResponse(BaseModel):
    metric: str
    observed: Optional[float] = None
    baseline_median: float
    baseline_mad: float
    absolute_deviation: Optional[float] = None
    relative_deviation_pct: Optional[float] = None
    robust_z_score: Optional[float] = None
    is_missing: bool = False
    sleep_deficit_hours: Optional[float] = None

class RecoveryDebtResponse(BaseModel):
    recovery_burden_score: float
    contributing_factors: List[str]
    subscores: Dict[str, float]
    disclaimer: str

class TrajectoryMetricResponse(BaseModel):
    metric: str
    direction: str # STABLE, IMPROVING, DETERIORATING
    slope: float
    volatility: float
    data_points: int
    interpretation: str

class TrajectorySummaryResponse(BaseModel):
    overall_direction: str
    overall_summary: str
    hrv_trajectory: TrajectoryMetricResponse
    sleep_trajectory: TrajectoryMetricResponse
    resting_hr_trajectory: TrajectoryMetricResponse
    observation_days: int

class ZoneIntelligenceResponse(BaseModel):
    operational_zone: str
    zone_code: str
    primary_features: List[str]
    key_analytical_question: str
    zone_specific_insights: List[str]
    is_risk_level: bool = False
    methodology_note: str

class PersonalStateResponse(BaseModel):
    personnel_id: str
    timestamp: datetime
    operational_zone: str
    duty_type: str
    shift: str
    baselines: Dict[str, BaselineMetricResponse]
    deviations: Dict[str, MetricDeviationResponse]
    trajectories: TrajectorySummaryResponse
    recovery_debt: RecoveryDebtResponse
    rebound_status: str
    transition_state: Dict[str, Any]
    evidence_quality: str
    attribution_summary: str
    processing_version: str = "v1.0"
    data_classification: str = "SYNTHETIC_DEMO_DATA"
