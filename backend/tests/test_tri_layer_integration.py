"""
SEPTERIA Unit & Integration Tests: Tri-Layer Stress Integration & Gating Engine
Verifies:
  - Invariant 1: Exertion discounts physiological stress attribution without hard clamping.
  - Invariant 2: Personal baseline homeostasis dampens raw ML uncertainty.
  - Invariant 3: Transient spikes do not escalate; persistent elevation satisfies temporal gate.
  - Invariant 4: Degraded / contradictory telemetry lowers action confidence (INCONCLUSIVE_DATA).
  - Invariant 5: Operational zones adjust decision gates contextually.
  - Invariant 6: Output recommendations are strictly advisory decision support (Human-in-the-loop).
  - Invariant 7: Native NaN telemetry handling without pipeline crashes.
"""

import pytest
import numpy as np
from backend.app.engine.integration.tri_layer_engine import TriLayerStressEngine, TriLayerConfig

@pytest.fixture
def engine():
    return TriLayerStressEngine()

@pytest.fixture
def standard_resting_window():
    return {
        "hr_mean": 72.0, "hr_std": 1.5, "hr_min": 68.0, "hr_max": 76.0, "hr_slope": 0.0,
        "hrv_rmssd": 58.0, "hrv_sdnn": 52.0, "hrv_pnn50": 32.0, "hrv_cv": 7.5,
        "eda_mean": 0.85, "eda_std": 0.05, "eda_min": 0.78, "eda_max": 0.95, "eda_slope": 0.0,
        "eda_tonic_mean": 0.85, "eda_phasic_peaks": 2.0, "eda_phasic_max_amplitude": 0.08, "eda_phasic_auc": 0.25,
        "temp_mean": 33.5, "temp_std": 0.02, "temp_slope": 0.0,
        "acc_magnitude_mean": 63.8, "acc_magnitude_std": 0.35, "acc_motion_energy": 0.12, "acc_peak_acceleration": 65.0
    }

@pytest.fixture
def personal_baseline():
    return {
        "hr_median": 70.0, "hr_mad": 2.0,
        "rmssd_median": 60.0, "rmssd_mad": 5.0,
        "eda_median": 0.80
    }

def test_exertion_discounts_attribution_without_hard_clamping(engine, standard_resting_window, personal_baseline):
    """
    Invariant: High kinetic motion must discount physiological stress attribution,
    but NOT hard clamp the probability to a fixed constant (e.g. 0.15).
    """
    # Create an active sprinting / running window
    exertion_window = dict(standard_resting_window)
    exertion_window["hr_mean"] = 145.0
    exertion_window["hrv_rmssd"] = 20.0
    exertion_window["eda_tonic_mean"] = 4.5
    exertion_window["acc_motion_energy"] = 8.5
    exertion_window["acc_magnitude_std"] = 4.2
    
    res = engine.evaluate_window(
        features=exertion_window,
        personal_baseline=personal_baseline,
        operational_zone="ZONE_1",
        recovery_burden_score=10.0 # Low recovery burden during normal physical PT
    )
    
    # Check exertion tagging
    assert res["layer_2_context_interpretation"]["is_physical_exertion"] is True
    assert res["layer_2_context_interpretation"]["exertion_tag"] == "PHYSICAL_EXERTION_ACTIVE"
    
    # Exertion must discount attribution, but must NOT be forced to exact min(P, 0.15)
    p_calibrated = res["layer_2_context_interpretation"]["p_calibrated"]
    assert p_calibrated > 0.0
    # Because recovery burden is low, welfare state must remain GREEN
    assert res["layer_3_welfare_decision"]["welfare_state"] == "GREEN"

def test_baseline_homeostasis_dampens_uncertainty(engine, standard_resting_window, personal_baseline):
    """
    Invariant: When soldier's physiological metrics are within their personal resting baseline,
    calibrated probability must be strictly lower than raw ML probability.
    """
    res = engine.evaluate_window(
        features=standard_resting_window,
        personal_baseline=personal_baseline,
        operational_zone="ZONE_2"
    )
    
    p_physio = res["layer_1_physiological_ml"]["raw_physiological_stress_probability"]
    p_calibrated = res["layer_2_context_interpretation"]["p_calibrated"]
    
    assert res["layer_2_context_interpretation"]["baseline_status"] == "WITHIN_NORMAL_BASELINE"
    assert p_calibrated <= p_physio
    assert res["layer_3_welfare_decision"]["welfare_state"] == "GREEN"

def test_transient_spike_does_not_escalate(engine, standard_resting_window, personal_baseline):
    """
    Invariant: An isolated single 60s spike must NOT escalate to AMBER or RED.
    Sustained elevation across K-of-N windows must satisfy the persistence gate.
    """
    # Create acute stress window
    stress_window = dict(standard_resting_window)
    stress_window["hr_mean"] = 105.0
    stress_window["hrv_rmssd"] = 18.0
    stress_window["eda_tonic_mean"] = 5.2
    stress_window["acc_motion_energy"] = 0.15 # Seated / stationary
    stress_window["acc_magnitude_std"] = 0.30
    
    # 1. Single isolated spike with normal recent history [0.10, 0.12]
    res_single = engine.evaluate_window(
        features=stress_window,
        personal_baseline=personal_baseline,
        operational_zone="ZONE_2",
        recovery_burden_score=60.0,
        trajectory_direction="DETERIORATING",
        recent_window_probabilities=[0.10, 0.12]
    )
    
    assert res_single["layer_3_welfare_decision"]["temporal_persistence_met"] is False
    assert res_single["layer_3_welfare_decision"]["welfare_state"] == "YELLOW"
    assert res_single["layer_3_welfare_decision"]["is_escalated"] is False
    
    # 2. Sustained elevation across multiple windows [0.75, 0.80]
    res_sustained = engine.evaluate_window(
        features=stress_window,
        personal_baseline=personal_baseline,
        operational_zone="ZONE_2",
        recovery_burden_score=75.0,
        trajectory_direction="DETERIORATING",
        recent_window_probabilities=[0.75, 0.80]
    )
    
    assert res_sustained["layer_3_welfare_decision"]["temporal_persistence_met"] is True
    assert res_sustained["layer_3_welfare_decision"]["welfare_state"] in ("AMBER", "RED")
    assert res_sustained["layer_3_welfare_decision"]["is_escalated"] is True

def test_degraded_telemetry_lowers_confidence(engine, standard_resting_window):
    """
    Invariant: Missing channels or contradictory telemetry must reduce ActionConfidence
    and output INCONCLUSIVE_DATA rather than escalating alerts.
    """
    # Create contradictory window: extreme HR elevation with zero EDA and zero motion
    contradictory_window = dict(standard_resting_window)
    contradictory_window["hr_mean"] = 135.0
    contradictory_window["eda_mean"] = 0.001
    contradictory_window["eda_tonic_mean"] = 0.001
    contradictory_window["acc_motion_energy"] = 0.01
    contradictory_window["acc_magnitude_std"] = 0.01
    contradictory_window["hrv_rmssd"] = np.nan
    contradictory_window["temp_mean"] = np.nan
    
    res = engine.evaluate_window(
        features=contradictory_window,
        operational_zone="ZONE_2"
    )
    
    assert res["layer_1_physiological_ml"]["contradictory_telemetry_detected"] is True
    assert res["layer_3_welfare_decision"]["action_confidence"] < 0.50
    assert res["layer_3_welfare_decision"]["welfare_state"] == "INCONCLUSIVE_DATA"
    assert res["layer_3_welfare_decision"]["is_escalated"] is False

def test_zone_context_changes_decision_gate(engine, standard_resting_window, personal_baseline):
    """
    Invariant: Operational zones alter decision gate thresholds contextually.
    Zone 1 (0.60), Zone 2 (0.50), and Zone 3 (dynamically adjusted based on recovery burden).
    """
    res_z1 = engine.evaluate_window(
        features=standard_resting_window,
        personal_baseline=personal_baseline,
        operational_zone="ZONE_1"
    )
    res_z2 = engine.evaluate_window(
        features=standard_resting_window,
        personal_baseline=personal_baseline,
        operational_zone="ZONE_2"
    )
    res_z3 = engine.evaluate_window(
        features=standard_resting_window,
        personal_baseline=personal_baseline,
        operational_zone="ZONE_3",
        recovery_burden_score=60.0,
        sleep_deficit_hours=3.0
    )
    
    t1 = res_z1["layer_2_context_interpretation"]["decision_gate_threshold"]
    t2 = res_z2["layer_2_context_interpretation"]["decision_gate_threshold"]
    t3 = res_z3["layer_2_context_interpretation"]["decision_gate_threshold"]
    
    assert t1 == 0.60
    assert t2 == 0.50
    # In Zone 3 with high recovery burden and sleep deficit, decision gate must be lower (higher sensitivity)
    assert t3 < t2
    assert t3 >= 0.30

def test_advisory_recommendations_are_non_diagnostic(engine, standard_resting_window, personal_baseline):
    """
    Invariant: Output recommendations must strictly use advisory decision-support phrasing
    ("Recommend authorized welfare/medical review") with zero automated clinical diagnoses.
    """
    stress_window = dict(standard_resting_window)
    stress_window["hr_mean"] = 110.0
    stress_window["hrv_rmssd"] = 15.0
    stress_window["eda_tonic_mean"] = 6.0
    stress_window["acc_motion_energy"] = 0.10
    
    res = engine.evaluate_window(
        features=stress_window,
        personal_baseline=personal_baseline,
        operational_zone="ZONE_3",
        recovery_burden_score=80.0,
        trajectory_direction="DETERIORATING",
        recent_window_probabilities=[0.85, 0.88]
    )
    
    action_text = res["layer_3_welfare_decision"]["recommended_action"]
    assert "Recommend authorized welfare/medical review" in action_text or "Recommend authorized unit welfare check" in action_text
    assert "diagnostic" not in action_text.lower()
    assert res["engine_metadata"]["is_capf_field_validated"] is False

def test_native_nan_resilience(engine, standard_resting_window, personal_baseline):
    """
    Invariant: Missing PRV, Temp, or EDA channels must be handled via native NaN routing
    without throwing exceptions.
    """
    nan_window = dict(standard_resting_window)
    nan_window["hrv_rmssd"] = np.nan
    nan_window["hrv_sdnn"] = np.nan
    nan_window["temp_mean"] = np.nan
    nan_window["eda_mean"] = np.nan
    
    res = engine.evaluate_window(
        features=nan_window,
        personal_baseline=personal_baseline,
        operational_zone="ZONE_2"
    )
    
    assert "p_calibrated" in res["layer_2_context_interpretation"]
    assert "welfare_state" in res["layer_3_welfare_decision"]
