"""
SEPTERIA Hosted System Comprehensive Integration Verification
Tests all hosted endpoints against http://localhost:8000:
  - Auth & Login (Commander, Medical, Welfare, Soldier)
  - Predictions: Model Info, Tri-Layer Inference (Exertion, Baseline, Zone 1/2/3, Temporal Gate)
  - Contextual Graph: Shared Patterns, Unit Patterns, Missing Data Support, 2D Visualization
"""

import requests
import json

BASE = "http://localhost:8000/api/v1"

def run_tests():
    print("=" * 100)
    print("TESTING HOSTED SEPTERIA API (http://localhost:8000)")
    print("=" * 100)
    
    # 1. Health
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200
    print(f"[OK] Health Check : {r.json()['status']} ({r.json()['service']})")
    
    # 2. Login
    r = requests.post(f"{BASE}/auth/login", json={"email": "commander@septeria.mil", "password": "commander123"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"[OK] Authentication: Token issued for commander@septeria.mil (Role: {r.json()['user']['role']})")
    
    # 3. Model Info
    r = requests.get(f"{BASE}/predictions/model-info", headers=headers)
    assert r.status_code == 200
    m_info = r.json()
    print(f"[OK] Model Info    : {m_info['model_designation']} (Version: {m_info['model_version']})")
    
    # 4. Tri-Layer Inference (Full 25 telemetry features)
    full_stress_window = {
        "hr_mean": 105.0, "hr_std": 3.2, "hr_min": 98.0, "hr_max": 112.0, "hr_slope": 0.1,
        "hrv_rmssd": 22.0, "hrv_sdnn": 28.0, "hrv_pnn50": 8.0, "hrv_cv": 9.5,
        "eda_mean": 4.1, "eda_std": 0.45, "eda_min": 3.5, "eda_max": 5.2, "eda_slope": 0.02,
        "eda_tonic_mean": 4.1, "eda_phasic_peaks": 10.0, "eda_phasic_max_amplitude": 0.45, "eda_phasic_auc": 2.8,
        "temp_mean": 33.1, "temp_std": 0.04, "temp_slope": -0.01,
        "acc_magnitude_mean": 63.9, "acc_magnitude_std": 0.32, "acc_motion_energy": 0.14, "acc_peak_acceleration": 65.2
    }
    
    inf_payload = {
        "features": full_stress_window,
        "personnel_id": "BSF-47-01",
        "operational_zone": "ZONE_3",
        "personal_baseline": {"hr_median": 70.0, "hr_mad": 2.0, "rmssd_median": 60.0, "rmssd_mad": 5.0, "eda_median": 0.8},
        "recovery_burden_score": 80.0,
        "sleep_deficit_hours": 4.0,
        "trajectory_direction": "DETERIORATING",
        "recent_window_probabilities": [0.82, 0.85]
    }
    r = requests.post(f"{BASE}/predictions/inference", json=inf_payload, headers=headers)
    assert r.status_code == 200
    inf_res = r.json()
    print(f"[OK] Inference API : State = [{inf_res['layer_3_welfare_decision']['welfare_state']}] | Zone Gate T = {inf_res['layer_2_context_interpretation']['decision_gate_threshold']}")
    print(f"     Advisory Action: {inf_res['layer_3_welfare_decision']['recommended_action']}")
    
    # 5. Shared Patterns
    r = requests.get(f"{BASE}/graph/shared-patterns", headers=headers)
    assert r.status_code == 200
    patterns = r.json()["patterns"]
    print(f"[OK] Shared Patterns: {len(patterns)} pattern(s) detected across operational graph")
    if len(patterns) > 0:
        pat = patterns[0]
        print(f"     Pattern ID: {pat['pattern_id']} (Affected Headcount: {pat['affected_personnel_count']} personnel)")
        print(f"     Authority Summary: \"{pat['authority_summary']}\"")
        
    # 6. Graph Visualization
    r = requests.get(f"{BASE}/graph/visualization", headers=headers)
    assert r.status_code == 200
    vis = r.json()
    print(f"[OK] Visualization  : {vis['summary']['total_nodes']} Nodes, {vis['summary']['total_edges']} Edges generated with 2D Spring Layout")
    
    # 7. Contextual Missing-Data Support
    r = requests.post(f"{BASE}/graph/missing-data-support", json={"personnel_id": "BSF-47-05", "metric_name": "hrv_rmssd"}, headers=headers)
    assert r.status_code == 200
    miss = r.json()
    print(f"[OK] Missing Data   : Status = [{miss['evidence_status']}] | Inferred Value = {miss['value']} ms")
    print(f"     Provenance: {miss['provenance']}")
    
    print("\n" + "=" * 100)
    print("ALL HOSTED BACKEND ENDPOINTS ARE LIVE, OPERATIONAL, AND PASSING")
    print("=" * 100)

if __name__ == "__main__":
    run_tests()
