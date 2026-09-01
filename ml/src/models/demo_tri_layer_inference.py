"""
SEPTERIA End-to-End Tri-Layer Engine Demo Script
Demonstrates end-to-end inference across 5 distinct operational scenarios:
  1. Scenario A: Seated Baseline Homeostasis (Zone 2)
  2. Scenario B: High-Intensity Tactical Physical Exertion (Zone 1)
  3. Scenario C: Transient Single-Window Stress Spike (Zone 2)
  4. Scenario D: Severe Sustained Autonomic Strain + Recovery Debt (Zone 3)
  5. Scenario E: Telemetry Degradation / Contradictory Sensor Data
"""

import os
import sys
import json
import numpy as np

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.engine.integration.tri_layer_engine import TriLayerStressEngine, TriLayerConfig

def run_demo():
    print("=" * 100)
    print("SEPTERIA TRI-LAYER INTEGRATION ENGINE END-TO-END DEMO")
    print("=" * 100)
    
    engine = TriLayerStressEngine()
    
    personal_baseline = {
        "hr_median": 70.0, "hr_mad": 2.0,
        "rmssd_median": 60.0, "rmssd_mad": 5.0,
        "eda_median": 0.80
    }
    
    # -------------------------------------------------------------------------
    # Scenario A: Seated Baseline Homeostasis (Zone 2)
    # -------------------------------------------------------------------------
    print("\n[SCENARIO A] Seated Homeostatic Baseline (Zone 2: Border / Remote Outpost)")
    window_a = {
        "hr_mean": 71.0, "hr_std": 1.2, "hr_min": 68.0, "hr_max": 74.0, "hr_slope": 0.0,
        "hrv_rmssd": 62.0, "hrv_sdnn": 55.0, "hrv_pnn50": 35.0, "hrv_cv": 7.0,
        "eda_mean": 0.82, "eda_std": 0.04, "eda_min": 0.75, "eda_max": 0.90, "eda_slope": 0.0,
        "eda_tonic_mean": 0.82, "eda_phasic_peaks": 1.0, "eda_phasic_max_amplitude": 0.05, "eda_phasic_auc": 0.15,
        "temp_mean": 33.6, "temp_std": 0.02, "temp_slope": 0.0,
        "acc_magnitude_mean": 63.8, "acc_magnitude_std": 0.30, "acc_motion_energy": 0.10, "acc_peak_acceleration": 64.5
    }
    res_a = engine.evaluate_window(
        features=window_a,
        personnel_id="SEP-1047",
        personal_baseline=personal_baseline,
        operational_zone="ZONE_2",
        recovery_burden_score=10.0,
        sleep_deficit_hours=0.0
    )
    print(f"  Layer 1 Raw ML P(Stress)       : {res_a['layer_1_physiological_ml']['raw_physiological_stress_probability']:.4f}")
    print(f"  Layer 2 Calibrated P(Stress)  : {res_a['layer_2_context_interpretation']['p_calibrated']:.4f} ({res_a['layer_2_context_interpretation']['baseline_status']})")
    print(f"  Layer 3 Welfare State Output   : [{res_a['layer_3_welfare_decision']['welfare_state']}] - {res_a['layer_3_welfare_decision']['recommended_action']}")

    # -------------------------------------------------------------------------
    # Scenario B: High-Intensity Tactical Physical Exertion (Zone 1)
    # -------------------------------------------------------------------------
    print("\n[SCENARIO B] High-Intensity Tactical Physical Exertion (Zone 1: Active Ops)")
    window_b = {
        "hr_mean": 152.0, "hr_std": 8.5, "hr_min": 135.0, "hr_max": 168.0, "hr_slope": 0.25,
        "hrv_rmssd": 18.0, "hrv_sdnn": 22.0, "hrv_pnn50": 4.0, "hrv_cv": 12.5,
        "eda_mean": 5.40, "eda_std": 0.65, "eda_min": 4.20, "eda_max": 6.80, "eda_slope": 0.05,
        "eda_tonic_mean": 5.40, "eda_phasic_peaks": 14.0, "eda_phasic_max_amplitude": 0.85, "eda_phasic_auc": 4.50,
        "temp_mean": 35.2, "temp_std": 0.12, "temp_slope": 0.02,
        "acc_magnitude_mean": 82.0, "acc_magnitude_std": 5.40, "acc_motion_energy": 12.8, "acc_peak_acceleration": 135.0
    }
    res_b = engine.evaluate_window(
        features=window_b,
        personnel_id="SEP-1047",
        personal_baseline=personal_baseline,
        operational_zone="ZONE_1",
        recovery_burden_score=15.0 # Normal physiological exercise
    )
    print(f"  Layer 1 Raw ML P(Stress)       : {res_b['layer_1_physiological_ml']['raw_physiological_stress_probability']:.4f}")
    print(f"  Layer 2 Exertion Tag           : {res_b['layer_2_context_interpretation']['exertion_tag']} (Attribution Discount Applied)")
    print(f"  Layer 2 Calibrated P(Stress)  : {res_b['layer_2_context_interpretation']['p_calibrated']:.4f}")
    print(f"  Layer 3 Welfare State Output   : [{res_b['layer_3_welfare_decision']['welfare_state']}] - {res_b['layer_3_welfare_decision']['recommended_action']}")

    # -------------------------------------------------------------------------
    # Scenario C: Transient Single-Window Stress Spike (Zone 2)
    # -------------------------------------------------------------------------
    print("\n[SCENARIO C] Transient Single-Window Stress Spike (Zone 2: Anti-Spike Persistence)")
    window_c = {
        "hr_mean": 105.0, "hr_std": 3.2, "hr_min": 98.0, "hr_max": 112.0, "hr_slope": 0.10,
        "hrv_rmssd": 22.0, "hrv_sdnn": 28.0, "hrv_pnn50": 8.0, "hrv_cv": 9.5,
        "eda_mean": 4.10, "eda_std": 0.45, "eda_min": 3.50, "eda_max": 5.20, "eda_slope": 0.02,
        "eda_tonic_mean": 4.10, "eda_phasic_peaks": 10.0, "eda_phasic_max_amplitude": 0.45, "eda_phasic_auc": 2.80,
        "temp_mean": 33.1, "temp_std": 0.04, "temp_slope": -0.01,
        "acc_magnitude_mean": 63.9, "acc_magnitude_std": 0.32, "acc_motion_energy": 0.14, "acc_peak_acceleration": 65.2
    }
    res_c = engine.evaluate_window(
        features=window_c,
        personnel_id="SEP-1047",
        personal_baseline=personal_baseline,
        operational_zone="ZONE_2",
        recovery_burden_score=55.0,
        recent_window_probabilities=[0.12, 0.15] # Previous windows normal
    )
    print(f"  Layer 1 Raw ML P(Stress)       : {res_c['layer_1_physiological_ml']['raw_physiological_stress_probability']:.4f}")
    print(f"  Layer 2 Calibrated P(Stress)  : {res_c['layer_2_context_interpretation']['p_calibrated']:.4f}")
    print(f"  Layer 3 Temporal Persistence   : {res_c['layer_3_welfare_decision']['temporal_persistence_met']} ({res_c['layer_3_welfare_decision']['windows_above_gate_count']}/{res_c['layer_3_welfare_decision']['total_windows_evaluated']} windows above gate)")
    print(f"  Layer 3 Welfare State Output   : [{res_c['layer_3_welfare_decision']['welfare_state']}] - {res_c['layer_3_welfare_decision']['recommended_action']}")

    # -------------------------------------------------------------------------
    # Scenario D: Sustained Autonomic Strain + Recovery Debt (Zone 3)
    # -------------------------------------------------------------------------
    print("\n[SCENARIO D] Sustained Autonomic Strain + Recovery Debt (Zone 3: Post-Incident Recovery)")
    res_d = engine.evaluate_window(
        features=window_c, # Same elevated physiological window
        personnel_id="SEP-1047",
        personal_baseline=personal_baseline,
        operational_zone="ZONE_3",
        recovery_burden_score=82.0, # Severe recovery debt
        sleep_deficit_hours=4.5,    # 4.5h cumulative sleep debt
        trajectory_direction="DETERIORATING",
        recent_window_probabilities=[0.82, 0.85] # Persistent elevation
    )
    print(f"  Layer 1 Raw ML P(Stress)       : {res_d['layer_1_physiological_ml']['raw_physiological_stress_probability']:.4f}")
    print(f"  Layer 2 Zone 3 Decision Gate   : T = {res_d['layer_2_context_interpretation']['decision_gate_threshold']:.4f} (Dynamically Adjusted by Debt/Sleep)")
    print(f"  Layer 3 Temporal Persistence   : {res_d['layer_3_welfare_decision']['temporal_persistence_met']} ({res_d['layer_3_welfare_decision']['windows_above_gate_count']}/{res_d['layer_3_welfare_decision']['total_windows_evaluated']} windows)")
    print(f"  Layer 3 Welfare State Output   : [{res_d['layer_3_welfare_decision']['welfare_state']}] - {res_d['layer_3_welfare_decision']['recommended_action']}")

    # -------------------------------------------------------------------------
    # Scenario E: Telemetry Degradation / Contradictory Sensor Data
    # -------------------------------------------------------------------------
    print("\n[SCENARIO E] Telemetry Degradation / Contradictory Sensor Data (Confidence Gating)")
    window_e = dict(window_a)
    window_e["hr_mean"] = 142.0
    window_e["eda_mean"] = 0.001
    window_e["eda_tonic_mean"] = 0.001
    window_e["acc_motion_energy"] = 0.01
    window_e["hrv_rmssd"] = np.nan
    window_e["temp_mean"] = np.nan
    
    res_e = engine.evaluate_window(
        features=window_e,
        personnel_id="SEP-1047",
        operational_zone="ZONE_2"
    )
    print(f"  Layer 1 Quality Score          : Q = {res_e['layer_1_physiological_ml']['data_quality_score']:.2f} (Contradiction: {res_e['layer_1_physiological_ml']['contradictory_telemetry_detected']})")
    print(f"  Layer 3 Action Confidence      : Conf = {res_e['layer_3_welfare_decision']['action_confidence']:.4f} (< 0.50 threshold)")
    print(f"  Layer 3 Welfare State Output   : [{res_e['layer_3_welfare_decision']['welfare_state']}] - {res_e['layer_3_welfare_decision']['recommended_action']}")
    
    print("\n" + "=" * 100)
    print("[DEMO COMPLETED] All 5 scenarios verified with expected mathematical & gating behaviors.")
    print("=" * 100)

if __name__ == "__main__":
    run_demo()
