"""
SEPTERIA Contextual Personnel Graph Demo Script (Phase 7)
Demonstrates:
  1. Graph building with 20 synthetic personnel across BSF Unit 47 (Zone 2, Night Deployment)
  2. Shared-pattern detection identifying 14 personnel with recovery deterioration
  3. Conservative Missing-Data Support:
     - Priority 1: Personal History first (Personnel 1) -> EVIDENCE_STATUS = PERSONAL_HISTORY
     - Priority 2: Contextual Cohort Imputation (Personnel 5) -> EVIDENCE_STATUS = INFERRED
     - Priority 3: Insufficient Evidence -> EVIDENCE_STATUS = MISSING
  4. Cold-Start Prior Decay for Personnel 18
  5. Privacy-Preserving Authority View (Commanders) vs Authorized Welfare View (Medical Officers)
  6. Graph Visualizer Data Summary (Nodes, Edges, 2D coordinates)
"""

import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.engine.graph.contextual_graph_engine import ContextualGraphEngine

def run_demo():
    print("=" * 100)
    print("SEPTERIA CONTEXTUAL PERSONNEL GRAPH DEMONSTRATION (PHASE 7)")
    print("=" * 100)
    
    engine = ContextualGraphEngine()
    
    # Setup BSF Unit 47 Cohort: 20 personnel in Zone 2 Night Deployment
    # 14 personnel exhibit deteriorating recovery trajectories and elevated recovery burden
    personnel_list = []
    for i in range(1, 21):
        is_deteriorating = (i <= 14)
        p_id = f"BSF-47-{i:02d}"
        
        # Samples: Personnel 1 has 4 samples, Personnel 5 has 0 samples (missing data test)
        if i == 5:
            samples = {"hrv_rmssd": [], "hr_mean": [72.0]}
        elif i == 18:
            samples = {"hrv_rmssd": [], "hr_mean": []} # Cold start
        else:
            samples = {"hrv_rmssd": [52.0, 56.0, 50.0, 58.0], "hr_mean": [68.0, 70.0, 72.0]}
            
        personnel_list.append({
            "personnel_id": p_id,
            "unit_id": "BSF-BN-47",
            "force": "BSF",
            "role": "Constable" if i > 2 else "Head Constable",
            "zone": "ZONE_2",
            "duty_type": "Night Patrol",
            "shift": "Night",
            "environment": "High Heat & Dust",
            "workload_level": "HIGH",
            "recovery_trajectory": "DETERIORATING" if is_deteriorating else "STABLE",
            "recovery_burden_score": 68.0 if is_deteriorating else 18.0,
            "history_days": 1 if i == 18 else 14, # Personnel 18 has 1 day history (cold start)
            "personal_history_samples": samples
        })
        
    unit_list = [
        {
            "unit_id": "BSF-BN-47",
            "name": "47th Battalion BSF",
            "force": "BSF",
            "station": "Rajasthan Border Outpost",
            "authorized_strength": 120
        }
    ]
    
    # 1. Build Graph
    print("\n[STEP 1] Constructing Contextual Graph...")
    g = engine.build_graph(personnel_list, unit_list)
    print(f"  Total Nodes in Graph : {len(g.nodes)} (Personnel, Unit, Zone, Shift, Duty)")
    print(f"  Total Contextual Edges: {len(g.edges)} (Structural & Contextual Similarity)")
    
    # 2. Shared-Pattern Detection
    print("\n[STEP 2] Running Shared-Pattern Detector...")
    patterns = engine.patterns
    print(f"  Shared Patterns Detected: {len(patterns)}")
    for p in patterns:
        print(f"\n  ---> Pattern ID: {p.pattern_id}")
        print(f"       Unit: {p.unit_id} | Zone: {p.operational_context['zone']} | Shift: {p.operational_context['shift']}")
        print(f"       Pattern Type: {p.pattern_type}")
        print(f"       Affected Personnel Headcount: {p.affected_personnel_count} of {len(personnel_list)} personnel")
        print(f"       Pattern Confidence: {p.confidence_level}")
        print(f"       Authority Summary (Command View): \"{p.authority_summary}\"")
        
    # 3. Missing-Data Support
    print("\n[STEP 3] Evaluating Contextual Missing-Data Support...")
    # Case 3A: Personnel 1 has personal history
    res_p1 = engine.get_contextual_missing_data_support("BSF-47-01", "hrv_rmssd")
    print(f"  Case A (Personnel BSF-47-01 - Has Personal History):")
    print(f"    Value: {res_p1['value']} ms | Status: [{res_p1['evidence_status']}] | Inferred: {res_p1['is_inferred']}")
    print(f"    Provenance: {res_p1['provenance']}")
    
    # Case 3B: Personnel 5 has missing history -> derives cohort inference
    res_p5 = engine.get_contextual_missing_data_support("BSF-47-05", "hrv_rmssd")
    print(f"\n  Case B (Personnel BSF-47-05 - Missing Personal History):")
    print(f"    Value: {res_p5['value']} ms | Status: [{res_p5['evidence_status']}] | Inferred: {res_p5['is_inferred']}")
    print(f"    Confidence: {res_p5['confidence']} | Provenance: {res_p5['provenance']}")
    
    # Case 3C: Unknown metric on non-existent cohort -> leaves missing
    res_unknown = engine.get_contextual_missing_data_support("UNKNOWN-SOLDIER", "hrv_rmssd")
    print(f"\n  Case C (Unknown Personnel - Insufficient Evidence):")
    print(f"    Value: {res_unknown['value']} | Status: [{res_unknown['evidence_status']}] | Inferred: {res_unknown['is_inferred']}")
    print(f"    Provenance: {res_unknown['provenance']}")
    
    # 4. Cold-Start Prior Decay
    print("\n[STEP 4] Evaluating Cold-Start Contextual Prior...")
    cold_p18 = engine.get_cold_start_prior("BSF-47-18") # 1 day history
    cold_p1 = engine.get_cold_start_prior("BSF-47-01")   # 14 days history
    print(f"  BSF-47-18 (History: {cold_p18['history_days']} day)  : is_cohort_prior = {cold_p18['is_cohort_prior']}, prior_weight = {cold_p18['prior_weight']} ({cold_p18['status']})")
    print(f"  BSF-47-01 (History: {cold_p1['history_days']} days): is_cohort_prior = {cold_p1['is_cohort_prior']}, prior_weight = {cold_p1['prior_weight']} ({cold_p1['status']})")
    
    # 5. Privacy & RBAC Views Comparison
    print("\n[STEP 5] Comparing Authority (Commander) vs Welfare (Medical Officer) Views...")
    pat = patterns[0]
    print("  --- COMMAND AUTHORITY VIEW (No Private Biometrics) ---")
    print(f"  Unit: {pat.unit_id}")
    print(f"  Context: Zone 2, Night Deployment")
    print(f"  Pattern: Shared Recovery Deterioration")
    print(f"  Personnel Affected: {pat.affected_personnel_count}")
    print(f"  Duration: {pat.duration_days} days | Confidence: {pat.confidence_level}")
    print(f"  Summary: {pat.authority_summary}")
    
    print("\n  --- AUTHORIZED WELFARE / MEDICAL VIEW (Authorized RBAC) ---")
    print(f"  Affected Personnel IDs: {pat.welfare_details['affected_personnel_ids']}")
    print(f"  Average Cohort Recovery Burden: {pat.welfare_details['average_recovery_burden']} / 100")
    print(f"  Primary Operational Drivers: {pat.welfare_details['primary_operational_drivers']}")
    print(f"  Recommended Follow-up: {pat.welfare_details['recommended_follow_up']}")
    
    # 6. Visualization Summary
    vis = engine.get_graph_visualization_data()
    print("\n[STEP 6] Graph Visualization Coordinate Generation:")
    print(f"  Generated {len(vis['nodes'])} 2D-positioned nodes and {len(vis['edges'])} edges with deterministic spring layout.")
    
    print("\n" + "=" * 100)
    print("[PHASE 7 DEMO COMPLETED SUCCESSFULLY]")
    print("=" * 100)

if __name__ == "__main__":
    run_demo()
