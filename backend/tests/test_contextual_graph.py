"""
SEPTERIA Contextual Personnel Graph Test Suite (Phase 7)
Verifies:
  1. Graph creation works.
  2. Same-unit relationship is created correctly.
  3. Same-zone relationship is created correctly.
  4. Similar workload relationship works.
  5. Shared deterioration is detected (BSF Unit 47 scenario).
  6. Missing data remains missing when contextual evidence is insufficient.
  7. Reconstructed data is marked INFERRED with explicit provenance.
  8. Cold-start prior is marked correctly (is_cohort_prior = True).
  9. Personal history takes priority over cohort prior.
  10. Raw peer health data is NOT exposed.
  11. RBAC blocks unauthorized graph access.
  12. Graph rebuild is deterministic for the same inputs.
"""

import pytest
import networkx as nx
import numpy as np
from backend.app.engine.graph.contextual_graph_engine import ContextualGraphEngine, SharedPatternResult

@pytest.fixture
def sample_personnel():
    return [
        {
            "personnel_id": f"BSF-47-{i:02d}",
            "unit_id": "BSF-BN-47",
            "force": "BSF",
            "role": "Constable",
            "zone": "ZONE_2",
            "duty_type": "Night Patrol",
            "shift": "Night",
            "environment": "High Heat & Dust",
            "workload_level": "HIGH",
            "recovery_trajectory": "DETERIORATING" if i <= 14 else "STABLE",
            "recovery_burden_score": 68.0 if i <= 14 else 22.0,
            "history_days": 14 if i != 18 else 1, # Personnel 18 is in cold-start
            "personal_history_samples": {
                "hrv_rmssd": [55.0, 58.0, 52.0, 60.0] if i not in (5, 18) else [],
                "hr_mean": [68.0, 70.0, 72.0]
            }
        }
        for i in range(1, 21) # 20 personnel in Unit 47, 14 deteriorating
    ]

@pytest.fixture
def sample_units():
    return [
        {
            "unit_id": "BSF-BN-47",
            "name": "47th Battalion BSF",
            "force": "BSF",
            "station": "Rajasthan Border Outpost",
            "authorized_strength": 120
        }
    ]

def test_1_graph_creation_works(sample_personnel, sample_units):
    """Verifies that the NetworkX graph initializes and populates nodes and edges."""
    engine = ContextualGraphEngine()
    g = engine.build_graph(sample_personnel, sample_units)
    
    assert isinstance(g, nx.Graph)
    assert len(g.nodes) > 0
    assert len(g.edges) > 0
    # Must have personnel, unit, zone, shift, duty nodes
    assert g.has_node("unit_BSF-BN-47")
    assert g.has_node("zone_ZONE_2")
    assert g.has_node("shift_Night")
    assert g.has_node("duty_Night Patrol")
    assert g.has_node("personnel_BSF-47-01")

def test_2_same_unit_relationship_created(sample_personnel, sample_units):
    """Verifies that SAME_UNIT structural and similarity edges are correctly created."""
    engine = ContextualGraphEngine()
    g = engine.build_graph(sample_personnel, sample_units)
    
    # Structural edge from Personnel to Unit
    assert g.has_edge("personnel_BSF-47-01", "unit_BSF-BN-47")
    edge_data = g.get_edge_data("personnel_BSF-47-01", "unit_BSF-BN-47")
    assert edge_data["relationship_type"] == "BELONGS_TO"
    
    # Similarity edge between two personnel in same unit
    assert g.has_edge("personnel_BSF-47-01", "personnel_BSF-47-02")
    peer_edge = g.get_edge_data("personnel_BSF-47-01", "personnel_BSF-47-02")
    assert "SAME_UNIT" in peer_edge["relationship_type"]

def test_3_same_zone_relationship_created(sample_personnel, sample_units):
    """Verifies that SAME_ZONE relationship is established between peers in the same zone."""
    engine = ContextualGraphEngine()
    g = engine.build_graph(sample_personnel, sample_units)
    
    assert g.has_edge("personnel_BSF-47-01", "zone_ZONE_2")
    peer_edge = g.get_edge_data("personnel_BSF-47-01", "personnel_BSF-47-02")
    assert "SAME_ZONE" in peer_edge["relationship_type"]

def test_4_similar_workload_relationship_works(sample_personnel, sample_units):
    """Verifies that SIMILAR_WORKLOAD relationship is recognized for personnel sharing high workload."""
    engine = ContextualGraphEngine()
    g = engine.build_graph(sample_personnel, sample_units)
    
    peer_edge = g.get_edge_data("personnel_BSF-47-01", "personnel_BSF-47-02")
    assert "SIMILAR_WORKLOAD" in peer_edge["relationship_type"]

def test_5_shared_deterioration_detected(sample_personnel, sample_units):
    """
    Verifies that the shared pattern detector flags the 14 deteriorating personnel in Unit 47.
    """
    engine = ContextualGraphEngine()
    engine.build_graph(sample_personnel, sample_units)
    
    patterns = engine.patterns
    assert len(patterns) == 1
    
    pat = patterns[0]
    assert pat.unit_id == "BSF-BN-47"
    assert pat.pattern_type == "SHARED_RECOVERY_DETERIORATION"
    assert pat.affected_personnel_count == 14
    assert len(pat.affected_personnel_ids) == 14
    assert pat.confidence_level == "HIGH" # 14 / 20 = 70% affected
    assert "Shared recovery trajectory deterioration" in pat.authority_summary
    assert "BSF-47-01" in pat.affected_personnel_ids

def test_6_missing_data_remains_missing_when_evidence_insufficient():
    """
    Verifies that an unknown personnel with no personal history and no cohort evidence remains MISSING.
    """
    engine = ContextualGraphEngine()
    engine.build_graph([], []) # Empty graph
    
    res = engine.get_contextual_missing_data_support("UNKNOWN-SOLDIER", "hrv_rmssd")
    assert res["evidence_status"] == "MISSING"
    assert res["value"] is None
    assert res["is_inferred"] is False

def test_7_reconstructed_data_marked_inferred(sample_personnel, sample_units):
    """
    Verifies that Personnel 5 (missing personal history) derives a cohort estimate
    explicitly tagged with EVIDENCE_STATUS = INFERRED and proper provenance.
    """
    engine = ContextualGraphEngine()
    engine.build_graph(sample_personnel, sample_units)
    
    # Personnel 5 has empty personal history, but 18 peers in Unit 47 have HRV history
    res = engine.get_contextual_missing_data_support("BSF-47-05", "hrv_rmssd")
    assert res["evidence_status"] == "INFERRED"
    assert res["is_inferred"] is True
    assert res["value"] is not None
    assert "Inferred from contextual cohort" in res["provenance"]
    assert res["confidence"] == 0.65

def test_8_cold_start_prior_marked_correctly(sample_personnel, sample_units):
    """
    Verifies that Personnel 18 (history_days = 1) is tagged with is_cohort_prior = True
    and positive prior weight.
    """
    engine = ContextualGraphEngine()
    engine.build_graph(sample_personnel, sample_units)
    
    cold_res = engine.get_cold_start_prior("BSF-47-18")
    assert cold_res["is_cohort_prior"] is True
    assert cold_res["prior_weight"] > 0.0
    assert cold_res["status"] == "TEMPORARY_COHORT_PRIOR_ACTIVE"

def test_9_personal_history_takes_priority_over_cohort(sample_personnel, sample_units):
    """
    Verifies that Personnel 1 (has 4 historical samples) derives its baseline from
    personal history, NOT cohort inference.
    """
    engine = ContextualGraphEngine()
    engine.build_graph(sample_personnel, sample_units)
    
    res = engine.get_contextual_missing_data_support("BSF-47-01", "hrv_rmssd")
    assert res["evidence_status"] == "PERSONAL_HISTORY"
    assert res["is_inferred"] is False
    assert res["value"] == 56.5 # median of [55.0, 58.0, 52.0, 60.0]
    assert "Personal baseline history" in res["provenance"]

def test_10_raw_peer_health_data_not_exposed(sample_personnel, sample_units):
    """
    Verifies that graph nodes, edges, and authority summaries do NOT contain
    raw peer physiological values (HR, HRV, EDA, TEMP).
    """
    engine = ContextualGraphEngine()
    g = engine.build_graph(sample_personnel, sample_units)
    
    # Check node attributes
    for n_id, attrs in g.nodes(data=True):
        assert "raw_hr" not in attrs
        assert "hrv_rmssd" not in attrs
        assert "eda_mean" not in attrs
        
    # Check edge attributes
    for u, v, attrs in g.edges(data=True):
        assert "raw_hr" not in attrs
        assert "hrv_rmssd" not in attrs
        
    # Check authority summary
    pat = engine.patterns[0]
    assert "bpm" not in pat.authority_summary
    assert "ms" not in pat.authority_summary
    assert "microSiemens" not in pat.authority_summary

def test_11_rbac_blocks_unauthorized_graph_access():
    """
    Verifies that personnel role cannot access private welfare details in shared patterns.
    """
    from backend.app.models.user import User
    from shared.constants.roles import UserRole
    from backend.app.api.v1.graph import get_all_shared_patterns
    
    soldier_user = User(id="user-1", email="soldier@septeria.mil", role=UserRole.PERSONNEL.value)
    welfare_user = User(id="user-2", email="welfare@septeria.mil", role=UserRole.WELFARE_OFFICER.value)
    
    res_soldier = get_all_shared_patterns(current_user=soldier_user)
    assert res_soldier["is_welfare_view"] is False
    # Soldier view must not include welfare_details with individual IDs
    for p in res_soldier["patterns"]:
        assert "welfare_details" not in p
        
    res_welfare = get_all_shared_patterns(current_user=welfare_user)
    assert res_welfare["is_welfare_view"] is True
    # Welfare view includes authorized details
    for p in res_welfare["patterns"]:
        assert "welfare_details" in p
        assert len(p["welfare_details"]["affected_personnel_ids"]) > 0

def test_12_graph_rebuild_is_deterministic(sample_personnel, sample_units):
    """
    Verifies that rebuilding the graph multiple times with the same input produces
    identical node counts, edge counts, pattern counts, and visualization coordinates.
    """
    engine1 = ContextualGraphEngine()
    g1 = engine1.build_graph(sample_personnel, sample_units)
    vis1 = engine1.get_graph_visualization_data()
    
    engine2 = ContextualGraphEngine()
    g2 = engine2.build_graph(sample_personnel, sample_units)
    vis2 = engine2.get_graph_visualization_data()
    
    assert len(g1.nodes) == len(g2.nodes)
    assert len(g1.edges) == len(g2.edges)
    assert len(engine1.patterns) == len(engine2.patterns)
    assert vis1["summary"]["total_nodes"] == vis2["summary"]["total_nodes"]
    assert vis1["summary"]["total_edges"] == vis2["summary"]["total_edges"]
    
    # Check deterministic 2D coordinates for first node
    assert vis1["nodes"][0]["x"] == vis2["nodes"][0]["x"]
    assert vis1["nodes"][0]["y"] == vis2["nodes"][0]["y"]
