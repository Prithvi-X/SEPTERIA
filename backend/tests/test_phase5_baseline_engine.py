"""Comprehensive Automated Test Suite for Phase 5: Personal Baseline + 3-Zone Intelligence Engine.

Tests:
1. Robust non-Gaussian statistical calculations (median, MAD, robust modified Z-score)
2. Cold-start cohort prior resolution and configurable threshold
3. Conservative baseline adaptation and deterioration lock
4. Context-conditioned baseline expectation adjustments
5. Personal deviation engine (absolute, relative, robust Z-scores, missingness preservation)
6. Multi-horizon trajectory engine (direction, slope, persistence, volatility)
7. Recovery rebound vs persistent post-event deviation
8. Recovery debt composite score with configurable weights and explainable factors
9. 3-Zone operational intelligence (Zone 1, 2, 3 feature weighting & context neutrality)
10. Transition-state engine (Post-Leave Day X/14, deployment rotation)
11. Contextual rules & scientific attribution
12. API endpoints and strict RBAC isolation
13. Scenarios A through F verification
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.personnel import Personnel
from backend.app.models.baseline import Baseline
from backend.app.models.physiology import PhysiologicalRecord
from backend.app.models.operational_context import OperationalContext
from backend.app.engine import (
    RobustStats,
    ColdStartEngine,
    ConservativeAdaptationEngine,
    ContextAdjuster,
    PersonalBaselineEngine,
    PersonalDeviationEngine,
    TrajectoryEngine,
    RecoveryReboundEngine,
    RecoveryDebtEngine,
    ZoneIntelligenceEngine,
    TransitionEngine,
    ContextualRulesEngine,
    DEFAULT_MIN_OBSERVATIONS_THRESHOLD,
    DEFAULT_RECOVERY_DEBT_WEIGHTS,
)
from backend.app.services.personal_state_service import PersonalStateService
from backend.app.core.security import create_access_token

client = TestClient(app)

def get_auth_token(email: str) -> str:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None, f"User with email {email} must exist in test database"
        return create_access_token(subject=user.id, role=user.role, extra_claims={"email": user.email})
    finally:
        db.close()

# ==============================================================================
# 1. Robust Non-Gaussian Statistics Tests
# ==============================================================================

def test_robust_stats_calculations():
    # Test median, MAD, and robust Z-score with non-Gaussian sample
    values = [42.0, 50.0, 52.0, 54.0, 55.0, 56.0, 58.0, 60.0, 95.0] # 95 is an outlier
    summary = RobustStats.compute_robust_summary(values)
    
    assert summary["median"] == 55.0
    assert summary["mad"] == 3.0 # median of sorted |x - 55|: [0, 1, 1, 3, 3, 5, 5, 13, 40] -> index 4 is 3.0
    assert summary["count"] == 9
    
    # Robust modified Z-score on outlier: 0.6745 * (95 - 55) / MAD
    z_outlier = RobustStats.robust_z_score(95.0, 55.0, summary["mad"])
    assert z_outlier > 3.0 # Significantly flagged without distorting median

def test_robust_stats_empty_and_single():
    empty_summary = RobustStats.compute_robust_summary([])
    assert empty_summary["median"] == 0.0
    assert empty_summary["mad"] == 1.0
    
    single_summary = RobustStats.compute_robust_summary([50.0])
    assert single_summary["median"] == 50.0
    assert single_summary["mad"] == 0.5 # Minimum epsilon floor

# ==============================================================================
# 2. Cold-Start Engine & Configurable Threshold
# ==============================================================================

def test_cold_start_configurable_threshold():
    engine_default = ColdStartEngine()
    assert engine_default.min_observations == DEFAULT_MIN_OBSERVATIONS_THRESHOLD
    assert engine_default.is_cold_start(2) is True
    assert engine_default.is_cold_start(3) is False

    engine_custom = ColdStartEngine(min_observations=5)
    assert engine_custom.is_cold_start(4) is True
    assert engine_custom.is_cold_start(5) is False

def test_cold_start_cohort_prior_resolution():
    engine = ColdStartEngine()
    prior_bsf = engine.get_cohort_prior(metric="hrv_rmssd", force="BSF", zone="Zone 2")
    
    assert prior_bsf["is_cohort_prior"] is True
    assert prior_bsf["quality_rating"] == "LOW"
    assert prior_bsf["median"] == 52.0
    assert prior_bsf["mad"] == 8.0
    assert "Temporary contextual cohort prior" in prior_bsf["provenance_note"]

# ==============================================================================
# 3. Conservative Baseline Adaptation & Deterioration Protection
# ==============================================================================

def test_conservative_adaptation_deterioration_lock():
    engine = ConservativeAdaptationEngine()
    current_baseline = {
        "median": 55.0,
        "mad": 5.0,
        "observation_count": 14,
        "quality_rating": "GOOD",
        "is_cohort_prior": False,
    }
    
    # Simulating 4 days of progressive downward deterioration (HRV: 52 -> 48 -> 44 -> 40)
    deteriorating_daily_trends = [55.0, 52.0, 48.0, 44.0, 40.0]
    new_obs = [40.0, 41.0, 39.0, 40.0]
    
    updated = engine.update_baseline_conservative(
        current_baseline=current_baseline,
        new_observations=new_obs,
        metric="hrv_rmssd",
        recent_daily_trends=deteriorating_daily_trends,
    )
    
    # Baseline median MUST be preserved at 55.0 rather than crashing down to 40.0
    assert updated["median"] == 55.0
    assert "locked: persistent multi-day recovery deterioration detected" in updated["adaptation_note"]

def test_conservative_adaptation_normal_slow_drift():
    engine = ConservativeAdaptationEngine()
    current_baseline = {
        "median": 70.0,
        "mad": 4.0,
        "observation_count": 14,
        "quality_rating": "GOOD",
        "is_cohort_prior": False,
    }
    # Stable normal observations slightly higher
    new_obs = [72.0, 73.0, 71.0, 72.0]
    updated = engine.update_baseline_conservative(
        current_baseline=current_baseline,
        new_observations=new_obs,
        metric="hr",
        recent_daily_trends=[70.0, 71.0, 70.0, 72.0],
    )
    
    # Should apply conservative bounded update
    assert 70.0 <= updated["median"] <= 72.0
    assert updated["observation_count"] == 18

# ==============================================================================
# 4. Context-Conditioned Baseline Adjustments
# ==============================================================================

def test_context_adjuster_night_shift_and_heat():
    # Test Night Shift Sleep expectation
    sleep_adj = ContextAdjuster.adjust_expected_baseline(
        metric="sleep_hours",
        baseline_median=7.0,
        shift="Night (20:00 - 04:00)",
    )
    assert sleep_adj["has_context_adjustment"] is True
    assert sleep_adj["context_adjusted_expected"] == 6.2 # -0.8h split sleep

    # Test High Heat Heart Rate adaptation
    heat_adj = ContextAdjuster.adjust_expected_baseline(
        metric="hr",
        baseline_median=72.0,
        environment="Arid / High Heat",
    )
    assert heat_adj["has_context_adjustment"] is True
    assert heat_adj["context_adjusted_expected"] == 76.0 # +4 bpm thermal strain

# ==============================================================================
# 5. Personal Deviation Engine
# ==============================================================================

def test_personal_deviation_calculations():
    baselines = {
        "hrv_rmssd": {"median": 55.0, "mad": 5.0},
        "resting_hr": {"median": 60.0, "mad": 3.0},
        "sleep_hours": {"median": 7.0, "mad": 0.8},
        "activity": {"median": 7000.0, "mad": 1000.0},
    }
    current_obs = {
        "hrv": 42.0,
        "resting_hr": 66.0,
        "sleep": 5.2,
        "activity": 6800.0,
    }
    
    deviations = PersonalDeviationEngine.compute_all_deviations(current_obs, baselines)
    
    # HRV: (42 - 55) = -13.0, (-13 / 55) * 100 = -23.6%
    assert deviations["hrv"]["absolute_deviation"] == -13.0
    assert deviations["hrv"]["relative_deviation_pct"] == -23.6
    assert deviations["hrv"]["robust_z_score"] < -1.5
    
    # Sleep: deficit = 7.0 - 5.2 = 1.8h
    assert deviations["sleep"]["sleep_deficit_hours"] == 1.8
    assert deviations["sleep"]["relative_deviation_pct"] == -25.7

def test_personal_deviation_missing_value_preservation():
    baselines = {
        "hrv_rmssd": {"median": 55.0, "mad": 5.0},
        "resting_hr": {"median": 60.0, "mad": 3.0},
        "sleep_hours": {"median": 7.0, "mad": 0.8},
    }
    current_obs = {"hrv": None, "resting_hr": 60.0, "sleep": None}
    deviations = PersonalDeviationEngine.compute_all_deviations(current_obs, baselines)
    
    assert deviations["hrv"]["is_missing"] is True
    assert deviations["hrv"]["observed"] is None
    assert deviations["hrv"]["robust_z_score"] is None

# ==============================================================================
# 6. Multi-Horizon Trajectory & Persistence Engine
# ==============================================================================

def test_trajectory_engine_directions_and_persistence():
    # Deteriorating HRV (58 -> 55 -> 51 -> 47 -> 43)
    det_vals = [58.0, 55.0, 51.0, 47.0, 43.0]
    det_traj = TrajectoryEngine.evaluate_metric_trajectory(det_vals, metric_name="hrv", higher_is_better=True)
    assert det_traj["direction"] == "DETERIORATING"
    assert det_traj["slope"] < -2.0
    
    # Improving HRV (42 -> 46 -> 50 -> 54 -> 56)
    imp_vals = [42.0, 46.0, 50.0, 54.0, 56.0]
    imp_traj = TrajectoryEngine.evaluate_metric_trajectory(imp_vals, metric_name="hrv", higher_is_better=True)
    assert imp_traj["direction"] == "IMPROVING"
    assert imp_traj["slope"] > 2.0
    
    # Stable Resting HR (61 -> 62 -> 61 -> 61 -> 62)
    stable_vals = [61.0, 62.0, 61.0, 61.0, 62.0]
    stable_traj = TrajectoryEngine.evaluate_metric_trajectory(stable_vals, metric_name="resting_hr", higher_is_better=False)
    assert stable_traj["direction"] == "STABLE"

    # Persistence of negative deviations
    deviations = [0.0, -1.0, -5.0, -8.0, -12.0, -14.0]
    persistence = TrajectoryEngine.calculate_persistence(deviations, expected_negative_is_bad=True)
    assert persistence == 4 # 4 consecutive negative deviations < -2.0

# ==============================================================================
# 7. Recovery Rebound vs. Persistent Deviation
# ==============================================================================

def test_recovery_rebound_observed():
    # 12 hours after critical incident, HR returned close to baseline
    res = RecoveryReboundEngine.evaluate_rebound(
        incident_occurred=True,
        hours_since_incident=12.0,
        current_hr=74.0,
        current_hrv=50.0,
        baseline_hr=72.0,
        baseline_hrv=52.0,
        baseline_hrv_mad=6.0,
    )
    assert res["rebound_status"] == "REBOUND_OBSERVED"
    assert res["is_rebound"] is True
    assert res["is_persistent_deviation"] is False

def test_recovery_persistent_deviation():
    # 36 hours post incident with continued HR elevation & suppressed HRV
    res = RecoveryReboundEngine.evaluate_rebound(
        incident_occurred=True,
        hours_since_incident=36.0,
        current_hr=88.0, # +16 bpm
        current_hrv=32.0, # -20 ms
        baseline_hr=72.0,
        baseline_hrv=52.0,
        baseline_hrv_mad=6.0,
    )
    assert res["rebound_status"] == "PERSISTENT_DEVIATION"
    assert res["is_rebound"] is False
    assert res["is_persistent_deviation"] is True

# ==============================================================================
# 8. Recovery Debt / Accumulated Strain (Provisional Heuristic)
# ==============================================================================

def test_recovery_debt_composite_calculation():
    engine = RecoveryDebtEngine()
    debt = engine.calculate_recovery_debt(
        sleep_deficit_hours=1.5, # 50% of sleep max
        hrv_suppression_pct=25.0, # ~71% of HRV max
        rhr_elevation_bpm=6.0, # 50% of RHR max
        consecutive_high_workload_days=4, # 80% of workload max
        is_post_leave_transition=True,
        post_leave_day=3, # Day 3/14
    )
    
    assert 50.0 <= debt["recovery_burden_score"] <= 85.0
    assert len(debt["contributing_factors"]) >= 4
    assert "Provisional prototype indicator" in debt["disclaimer"]

# ==============================================================================
# 9. 3-Zone Operational Intelligence Engine
# ==============================================================================

def test_zone_intelligence_context_neutrality():
    engine = ZoneIntelligenceEngine()
    
    # Zone 1 evaluation
    z1_eval = engine.evaluate_zone_context(
        operational_zone="Zone 1: High-Intensity / Active Operations",
        deviations={},
        trajectories={},
        recovery_debt={},
        motion_context="HIGH",
    )
    assert z1_eval["zone_code"] == "ZONE_1"
    assert z1_eval["is_risk_level"] is False
    assert "Tactical active exertion expected in Zone 1" in z1_eval["zone_specific_insights"][0]
    
    # Zone 2 evaluation
    z2_eval = engine.evaluate_zone_context(
        operational_zone="Zone 2: Border / Remote / Extreme Environment",
        deviations={"sleep": {"sleep_deficit_hours": 1.5}},
        trajectories={},
        recovery_debt={},
    )
    assert z2_eval["zone_code"] == "ZONE_2"
    assert z2_eval["is_risk_level"] is False
    assert "Zone 2 cumulative sleep debt detected" in z2_eval["zone_specific_insights"][0]

# ==============================================================================
# 10. Transition-State Engine
# ==============================================================================

def test_transition_engine_post_leave_and_rotation():
    # Post-leave Day 3 / 14
    trans_leave = TransitionEngine.evaluate_leave_transition(
        leave_status="POST_LEAVE_TRANSITION",
        post_leave_day_count=3,
        total_transition_days=14,
    )
    assert trans_leave["is_transition_active"] is True
    assert trans_leave["current_day"] == 3
    assert trans_leave["adaptation_phase"] == "EARLY_ADAPTATION"

    # Temporary deployment rotation (5.5 days remaining of 7)
    trans_rot = TransitionEngine.evaluate_deployment_rotation(
        is_temporary=True,
        remaining_days=5.5,
        total_deployment_days=7.0,
    )
    assert trans_rot["is_transition_active"] is True
    assert trans_rot["rotation_phase"] == "DEPLOYMENT_START"

# ==============================================================================
# 11. Contextual Rules & Scientific Attribution Phrasing
# ==============================================================================

def test_contextual_rules_scientific_attribution():
    rules = ContextualRulesEngine()
    
    # High HR + High Activity -> Exertion attribution
    res_exertion = rules.formulate_attribution(
        hr_elevated=True,
        motion_context="EXERTIONAL",
        hrv_suppressed=False,
        sleep_deficit=False,
        sqi_status="GOOD",
    )
    assert res_exertion["is_exertion_explained"] is True
    assert "Physiological elevation is consistent with physical exertion; psychological attribution reduced." in res_exertion["summary"]

    # High HR + Low Activity -> Potential unexplained deviation
    res_unexplained = rules.formulate_attribution(
        hr_elevated=True,
        motion_context="LOW",
        hrv_suppressed=True,
        sleep_deficit=True,
        sqi_status="GOOD",
    )
    assert res_unexplained["is_exertion_explained"] is False
    assert "potential unexplained physiological deviation" in res_unexplained["summary"]

# ==============================================================================
# 12. API Endpoints & Strict RBAC Isolation Tests
# ==============================================================================

def test_personnel_me_baseline_and_state_endpoints():
    token = get_auth_token("personnel.p1047@septeria.gov.in")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. GET /personnel/me/baseline
    res_base = client.get("/api/v1/personnel/me/baseline", headers=headers)
    assert res_base.status_code == 200
    base_data = res_base.json()
    assert base_data["personnel_id"] == "P-1047"
    assert "hrv_rmssd" in base_data["baselines"]
    assert base_data["baselines"]["hrv_rmssd"]["median"] > 0
    assert base_data["baselines"]["hrv_rmssd"]["mad"] > 0

    # 2. GET /personnel/me/state
    res_state = client.get("/api/v1/personnel/me/state", headers=headers)
    assert res_state.status_code == 200
    state_data = res_state.json()
    assert state_data["personnel_id"] == "P-1047"
    assert "hrv" in state_data["deviations"]
    assert "recovery_debt" in state_data
    assert state_data["recovery_debt"]["recovery_burden_score"] >= 0

    # 3. GET /personnel/me/trajectory
    res_traj = client.get("/api/v1/personnel/me/trajectory", headers=headers)
    assert res_traj.status_code == 200
    traj_data = res_traj.json()
    assert "overall_direction" in traj_data

    # 4. GET /personnel/me/context-intelligence
    res_zone = client.get("/api/v1/personnel/me/context-intelligence", headers=headers)
    assert res_zone.status_code == 200
    zone_data = res_zone.json()
    assert zone_data["is_risk_level"] is False

def test_cross_personnel_access_and_rbac_enforcement():
    personnel_token = get_auth_token("personnel.p1047@septeria.gov.in")
    welfare_token = get_auth_token("welfare.crpf@septeria.gov.in")
    commander_token = get_auth_token("commander.bsf47@septeria.gov.in")

    # Personnel attempting to access authority personnel endpoint -> 403 Forbidden
    res_forbidden = client.get(
        "/api/v1/personnel/P-1047/state",
        headers={"Authorization": f"Bearer {personnel_token}"},
    )
    assert res_forbidden.status_code == 403

    # Authorized Welfare Officer accessing personnel state -> 200 OK
    res_welfare = client.get(
        "/api/v1/personnel/P-1047/state",
        headers={"Authorization": f"Bearer {welfare_token}"},
    )
    assert res_welfare.status_code == 200
    assert res_welfare.json()["personnel_id"] == "P-1047"

    # Commander accessing aggregated operational zone summary -> 200 OK
    res_comm_summary = client.get(
        "/api/v1/operations/zone-intelligence-summary",
        headers={"Authorization": f"Bearer {commander_token}"},
    )
    assert res_comm_summary.status_code == 200
    assert "zone_distribution" in res_comm_summary.json()

# ==============================================================================
# 13. Scenarios A through F Verification
# ==============================================================================

def test_scenario_a_normal_person(db_session=None):
    """Scenario A: Normal person with stable metrics."""
    baselines = {"hr": {"median": 72.0, "mad": 4.0}, "hrv_rmssd": {"median": 54.0, "mad": 6.0}, "sleep_hours": {"median": 7.2, "mad": 0.6}}
    current_obs = {"hr": 73.0, "hrv": 53.0, "sleep": 7.1, "activity": 6500.0, "motion_context": "MODERATE", "sqi_status": "GOOD"}
    
    devs = PersonalDeviationEngine.compute_all_deviations(current_obs, baselines)
    debt = RecoveryDebtEngine().calculate_recovery_debt(sleep_deficit_hours=0.1, hrv_suppression_pct=1.8, rhr_elevation_bpm=1.0)
    
    assert abs(devs["hrv"]["relative_deviation_pct"]) < 5.0
    assert debt["recovery_burden_score"] < 20.0

def test_scenario_b_physical_exertion():
    """Scenario B: High HR + High Activity -> Exertional context, reduced psychological attribution."""
    rules = ContextualRulesEngine()
    attr = rules.formulate_attribution(hr_elevated=True, motion_context="EXERTIONAL", hrv_suppressed=False, sleep_deficit=False)
    assert attr["is_exertion_explained"] is True
    assert "psychological attribution reduced" in attr["summary"]

def test_scenario_c_recovery_decline():
    """Scenario C: Sleep restriction + HRV drop + elevated RHR -> Deteriorating trajectory, rising debt."""
    det_history = [{"hrv": 54.0, "sleep": 7.0, "resting_hr": 60.0}, {"hrv": 49.0, "sleep": 5.5, "resting_hr": 63.0}, {"hrv": 44.0, "sleep": 4.5, "resting_hr": 66.0}]
    trajectories = TrajectoryEngine.compute_all_trajectories(det_history)
    debt = RecoveryDebtEngine().calculate_recovery_debt(sleep_deficit_hours=2.5, hrv_suppression_pct=22.0, rhr_elevation_bpm=6.0, consecutive_high_workload_days=3)
    
    assert trajectories["overall_direction"] == "DETERIORATING"
    assert debt["recovery_burden_score"] > 50.0

def test_scenario_d_post_leave_transition():
    """Scenario D: Post-leave Day 3/14 -> Transition context only, no automatic risk label."""
    trans = TransitionEngine.evaluate_leave_transition(leave_status="POST_LEAVE_TRANSITION", post_leave_day_count=3)
    assert trans["is_transition_active"] is True
    assert trans["current_day"] == 3
    assert trans["adaptation_phase"] == "EARLY_ADAPTATION"

def test_scenario_e_post_incident_rebound():
    """Scenario E: Acute response followed by return toward baseline in 12h -> Recovery rebound observed."""
    reb = RecoveryReboundEngine.evaluate_rebound(incident_occurred=True, hours_since_incident=12.0, current_hr=73.0, current_hrv=51.0, baseline_hr=72.0, baseline_hrv=52.0, baseline_hrv_mad=6.0)
    assert reb["rebound_status"] == "REBOUND_OBSERVED"
    assert reb["is_rebound"] is True

def test_scenario_f_poor_post_incident_recovery():
    """Scenario F: Persistent HR elevation and suppressed HRV 36h post event -> Persistent recovery deviation."""
    reb = RecoveryReboundEngine.evaluate_rebound(incident_occurred=True, hours_since_incident=36.0, current_hr=86.0, current_hrv=33.0, baseline_hr=72.0, baseline_hrv=52.0, baseline_hrv_mad=6.0)
    assert reb["rebound_status"] == "PERSISTENT_DEVIATION"
    assert reb["is_persistent_deviation"] is True
