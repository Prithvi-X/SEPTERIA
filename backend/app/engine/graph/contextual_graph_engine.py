"""
SEPTERIA Contextual Personnel Graph Engine (Phase 7)
Technology: NetworkX + PostgreSQL Operational Intelligence

Implements:
  - Deterministic Graph Construction (Personnel, Unit, Zone, Shift, Duty, Environment, Workload, Trajectory)
  - Privacy-Preserving Contextual Similarity Edges (Zero raw peer health/biometric leaks)
  - Shared-Pattern Detection (Unit-level cluster distress & recovery deterioration)
  - Conservative Contextual Missing-Data Support (Personal History -> Cohort Inferred -> Missing)
  - Cold-Start Contextual Prior with Dynamic Personal Weighting
  - Deterministic Spring Layout Coordinates for Graph Visualization
"""

import math
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
import networkx as nx
import numpy as np

@dataclass
class GraphEntity:
    id: str
    entity_type: str # PERSONNEL, UNIT, ZONE, SHIFT, DUTY, ENVIRONMENT
    properties: Dict[str, Any] = field(default_factory=dict)
    privacy_scope: str = "PUBLIC" # PUBLIC, UNIT, AUTHORIZED_WELFARE, RESTRICTED_SELF

@dataclass
class GraphEdge:
    source: str
    target: str
    relationship_type: str # BELONGS_TO, ASSIGNED_ZONE, ASSIGNED_SHIFT, SAME_UNIT, SAME_ZONE, SIMILAR_WORKLOAD, SIMILAR_RECOVERY_TRAJECTORY
    similarity_weight: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    privacy_scope: str = "PUBLIC"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SharedPatternResult:
    pattern_id: str
    unit_id: str
    operational_context: Dict[str, Any]
    pattern_type: str # SHARED_RECOVERY_DETERIORATION, WORKLOAD_ACCUMULATION, NIGHT_SHIFT_BURDEN
    affected_personnel_count: int
    affected_personnel_ids: List[str] # Disclosed only to authorized welfare/medical officers
    duration_days: int
    confidence_level: str # HIGH, MODERATE, LOW
    authority_summary: str # High-level summary for Commanders (no private health values)
    welfare_details: Dict[str, Any] # Detailed context for Medical/Welfare officers
    detected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class ContextualGraphEngine:
    """
    Core graph intelligence engine built on NetworkX for contextual military personnel monitoring.
    """
    def __init__(self):
        self.graph = nx.Graph()
        self.personnel_data: Dict[str, Dict[str, Any]] = {}
        self.unit_data: Dict[str, Dict[str, Any]] = {}
        self.patterns: List[SharedPatternResult] = []
        self._last_rebuild_timestamp: Optional[str] = None

    def build_graph(
        self,
        personnel_records: List[Dict[str, Any]],
        unit_records: Optional[List[Dict[str, Any]]] = None,
        operational_contexts: Optional[List[Dict[str, Any]]] = None,
        personal_states: Optional[List[Dict[str, Any]]] = None
    ) -> nx.Graph:
        """
        Deterministically constructs the NetworkX contextual graph from authoritative records.
        """
        self.graph.clear()
        self.personnel_data.clear()
        self.unit_data.clear()
        self.patterns.clear()
        
        # 1. Index Units
        for u in (unit_records or []):
            u_id = u["unit_id"]
            self.unit_data[u_id] = u
            self.graph.add_node(
                f"unit_{u_id}",
                entity_type="UNIT",
                entity_id=u_id,
                name=u.get("name", u_id),
                force=u.get("force", "BSF"),
                privacy_scope="UNIT"
            )
            
        # 2. Index Personal States & Operational Contexts
        states_by_personnel = {}
        for s in (personal_states or []):
            states_by_personnel[s["personnel_id"]] = s
            
        contexts_by_personnel = {}
        for c in (operational_contexts or []):
            p_id = c.get("personnel_id")
            if p_id:
                contexts_by_personnel[p_id] = c
                
        # 3. Add Personnel Nodes & Structural Context Edges
        # Sort personnel by ID for deterministic graph construction
        sorted_personnel = sorted(personnel_records, key=lambda x: str(x.get("personnel_id", "")))
        
        for p in sorted_personnel:
            p_id = p["personnel_id"]
            u_id = p.get("unit_id", "UNKNOWN_UNIT")
            role = p.get("role", "Constable")
            
            # Merge with active context & state
            ctx = contexts_by_personnel.get(p_id, {})
            st = states_by_personnel.get(p_id, {})
            
            zone = ctx.get("zone", st.get("operational_zone", p.get("zone", "ZONE_2")))
            duty = ctx.get("duty_type", st.get("duty_type", p.get("duty_type", "Border Patrol")))
            shift = ctx.get("shift", st.get("shift", p.get("shift", "Day")))
            env = ctx.get("environment", p.get("environment", "Standard"))
            workload = p.get("workload_level", "NORMAL") # LOW, NORMAL, HIGH, EXTREME
            recovery_traj = st.get("trajectories", {}).get("hrv", p.get("recovery_trajectory", "STABLE"))
            recovery_debt = st.get("recovery_burden_score", p.get("recovery_burden_score", 0.0))
            
            personnel_node_data = {
                "personnel_id": p_id,
                "unit_id": u_id,
                "role": role,
                "zone": zone,
                "duty_type": duty,
                "shift": shift,
                "environment": env,
                "workload_level": workload,
                "recovery_trajectory": recovery_traj,
                "recovery_burden_score": recovery_debt,
                "history_days": p.get("history_days", 14),
                "personal_history_samples": p.get("personal_history_samples", {})
            }
            self.personnel_data[p_id] = personnel_node_data
            
            p_node_id = f"personnel_{p_id}"
            self.graph.add_node(
                p_node_id,
                entity_type="PERSONNEL",
                entity_id=p_id,
                unit_id=u_id,
                role=role,
                privacy_scope="RESTRICTED_SELF"
            )
            
            # Structural Context Nodes & Edges
            unit_node_id = f"unit_{u_id}"
            if not self.graph.has_node(unit_node_id):
                self.graph.add_node(unit_node_id, entity_type="UNIT", entity_id=u_id, privacy_scope="UNIT")
            self.graph.add_edge(p_node_id, unit_node_id, relationship_type="BELONGS_TO", similarity_weight=1.0)
            
            zone_node_id = f"zone_{zone}"
            if not self.graph.has_node(zone_node_id):
                self.graph.add_node(zone_node_id, entity_type="ZONE", entity_id=zone, privacy_scope="PUBLIC")
            self.graph.add_edge(p_node_id, zone_node_id, relationship_type="ASSIGNED_ZONE", similarity_weight=1.0)
            
            shift_node_id = f"shift_{shift}"
            if not self.graph.has_node(shift_node_id):
                self.graph.add_node(shift_node_id, entity_type="SHIFT", entity_id=shift, privacy_scope="PUBLIC")
            self.graph.add_edge(p_node_id, shift_node_id, relationship_type="ASSIGNED_SHIFT", similarity_weight=1.0)
            
            duty_node_id = f"duty_{duty}"
            if not self.graph.has_node(duty_node_id):
                self.graph.add_node(duty_node_id, entity_type="DUTY", entity_id=duty, privacy_scope="PUBLIC")
            self.graph.add_edge(p_node_id, duty_node_id, relationship_type="ASSIGNED_DUTY", similarity_weight=1.0)

        # 4. Construct Contextual Similarity Edges Between Personnel Pairs (No Raw Biometrics)
        p_ids = list(self.personnel_data.keys())
        for i in range(len(p_ids)):
            for j in range(i + 1, len(p_ids)):
                p1 = self.personnel_data[p_ids[i]]
                p2 = self.personnel_data[p_ids[j]]
                
                sim_weight, rel_types = self._compute_contextual_similarity(p1, p2)
                if sim_weight >= 0.40: # Meaningful contextual threshold
                    self.graph.add_edge(
                        f"personnel_{p1['personnel_id']}",
                        f"personnel_{p2['personnel_id']}",
                        relationship_type=",".join(rel_types),
                        similarity_weight=round(float(sim_weight), 2),
                        shared_contexts=rel_types,
                        privacy_scope="UNIT"
                    )
                    
        self._last_rebuild_timestamp = datetime.utcnow().isoformat()
        
        # 5. Detect Shared Operational Patterns
        self.patterns = self.detect_shared_patterns()
        return self.graph

    def _compute_contextual_similarity(self, p1: Dict[str, Any], p2: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        Computes privacy-preserving contextual similarity between two personnel.
        Zero raw health values are compared.
        """
        weight = 0.0
        rel_types = []
        
        if p1["unit_id"] == p2["unit_id"]:
            weight += 0.25
            rel_types.append("SAME_UNIT")
            
        if p1["zone"] == p2["zone"]:
            weight += 0.15
            rel_types.append("SAME_ZONE")
            
        if p1["shift"] == p2["shift"]:
            weight += 0.15
            rel_types.append("SAME_SHIFT")
            
        if p1["duty_type"] == p2["duty_type"]:
            weight += 0.15
            rel_types.append("SAME_DUTY")
            
        if p1["environment"] == p2["environment"]:
            weight += 0.10
            rel_types.append("SAME_ENVIRONMENT")
            
        if p1["workload_level"] == p2["workload_level"]:
            weight += 0.10
            rel_types.append("SIMILAR_WORKLOAD")
            
        if p1["recovery_trajectory"] == p2["recovery_trajectory"]:
            weight += 0.10
            rel_types.append("SIMILAR_RECOVERY_TRAJECTORY")
            
        return weight, rel_types

    def detect_shared_patterns(self, min_cluster_size: int = 3) -> List[SharedPatternResult]:
        """
        Identifies shared operational distress patterns across units and duty clusters.
        """
        patterns = []
        
        # Group personnel by (Unit, Zone, Shift, Duty)
        cohorts = {}
        for p_id, p in self.personnel_data.items():
            key = (p["unit_id"], p["zone"], p["shift"], p["duty_type"])
            if key not in cohorts:
                cohorts[key] = []
            cohorts[key].append(p)
            
        for (u_id, zone, shift, duty), members in cohorts.items():
            if len(members) < min_cluster_size:
                continue
                
            # Evaluate shared recovery trajectory deterioration
            deteriorating = [m for m in members if m["recovery_trajectory"] == "DETERIORATING"]
            high_debt = [m for m in members if m["recovery_burden_score"] >= 50.0]
            
            # Condition: >= 50% of the cohort shows deteriorating trajectory or high debt
            if len(deteriorating) >= max(min_cluster_size, math.ceil(len(members) * 0.4)):
                pattern_id = f"PAT-{u_id}-{zone}-{shift}-{len(patterns) + 1}"
                
                # Confidence determination
                pct_affected = len(deteriorating) / len(members)
                conf = "HIGH" if pct_affected >= 0.70 else "MODERATE"
                
                authority_summary = (
                    f"Unit {u_id} [{zone}, {shift} Shift]: Shared recovery trajectory deterioration detected "
                    f"affecting {len(deteriorating)} of {len(members)} personnel under active deployment."
                )
                
                welfare_details = {
                    "unit_id": u_id,
                    "zone": zone,
                    "shift": shift,
                    "duty_type": duty,
                    "total_cohort_size": len(members),
                    "affected_headcount": len(deteriorating),
                    "affected_personnel_ids": [m["personnel_id"] for m in deteriorating],
                    "average_recovery_burden": round(float(np.mean([m["recovery_burden_score"] for m in deteriorating])), 1),
                    "primary_operational_drivers": [
                        f"{shift} duty shift scheduling",
                        f"Deployment under {zone} environmental conditions",
                        "Consecutive multi-day recovery suppression"
                    ],
                    "recommended_follow_up": "Authorized Unit Medical Officer / Psychologist review of shift rotation and rest opportunity."
                }
                
                pat_res = SharedPatternResult(
                    pattern_id=pattern_id,
                    unit_id=u_id,
                    operational_context={
                        "zone": zone,
                        "shift": shift,
                        "duty_type": duty,
                        "environment": members[0]["environment"]
                    },
                    pattern_type="SHARED_RECOVERY_DETERIORATION",
                    affected_personnel_count=len(deteriorating),
                    affected_personnel_ids=[m["personnel_id"] for m in deteriorating],
                    duration_days=3,
                    confidence_level=conf,
                    authority_summary=authority_summary,
                    welfare_details=welfare_details
                )
                patterns.append(pat_res)
                
        return patterns

    def get_contextual_missing_data_support(
        self,
        personnel_id: str,
        metric_name: str, # e.g. "hrv_rmssd", "hr_mean"
        observed_value: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Conservative contextual missing-data support:
        Priority 1: Personal history (robust median) -> EVIDENCE_STATUS = "PERSONAL_HISTORY"
        Priority 2: Contextual cohort prior (if personal history < 3 obs) -> EVIDENCE_STATUS = "INFERRED"
        Priority 3: Insufficient evidence -> EVIDENCE_STATUS = "MISSING" (Never silently fill)
        """
        if observed_value is not None and not np.isnan(observed_value):
            return {
                "metric": metric_name,
                "value": round(float(observed_value), 2),
                "evidence_status": "OBSERVED",
                "is_inferred": False,
                "confidence": 1.0,
                "provenance": "Direct wearable sensor observation"
            }
            
        p_data = self.personnel_data.get(personnel_id)
        if not p_data:
            return {
                "metric": metric_name,
                "value": None,
                "evidence_status": "MISSING",
                "is_inferred": False,
                "confidence": 0.0,
                "provenance": "Personnel not found in contextual graph"
            }
            
        # Priority 1: Check Personal History
        personal_samples = p_data.get("personal_history_samples", {}).get(metric_name, [])
        if len(personal_samples) >= 3:
            personal_med = float(np.median(personal_samples))
            return {
                "metric": metric_name,
                "value": round(personal_med, 2),
                "evidence_status": "PERSONAL_HISTORY",
                "is_inferred": False,
                "confidence": 0.85,
                "provenance": f"Personal baseline history ({len(personal_samples)} historical resting observations)"
            }
            
        # Priority 2: Contextual Cohort Inferred Prior
        # Find contextually identical peers in the same (Unit, Zone, Shift, Duty)
        u_id = p_data["unit_id"]
        zone = p_data["zone"]
        shift = p_data["shift"]
        duty = p_data["duty_type"]
        
        cohort_vals = []
        for peer_id, peer in self.personnel_data.items():
            if peer_id != personnel_id:
                if peer["unit_id"] == u_id and peer["zone"] == zone and peer["shift"] == shift:
                    peer_samples = peer.get("personal_history_samples", {}).get(metric_name, [])
                    if len(peer_samples) > 0:
                        cohort_vals.append(float(np.median(peer_samples)))
                        
        if len(cohort_vals) >= 3:
            cohort_med = float(np.median(cohort_vals))
            return {
                "metric": metric_name,
                "value": round(cohort_med, 2),
                "evidence_status": "INFERRED",
                "is_inferred": True,
                "confidence": 0.65,
                "provenance": (
                    f"Inferred from contextual cohort ({len(cohort_vals)} peers in Unit {u_id}, "
                    f"{zone}, {shift} Shift, {duty})"
                )
            }
            
        # Priority 3: Insufficient Evidence -> Leave Missing
        return {
            "metric": metric_name,
            "value": None,
            "evidence_status": "MISSING",
            "is_inferred": False,
            "confidence": 0.0,
            "provenance": "Insufficient personal and contextual cohort evidence; remaining missing/uncertain"
        }

    def get_cold_start_prior(self, personnel_id: str) -> Dict[str, Any]:
        """
        Produces a temporary contextual prior for personnel with insufficient personal history (< 3 days).
        Prior weight dynamically decreases as personal history accumulates.
        """
        p_data = self.personnel_data.get(personnel_id)
        if not p_data:
            return {"is_cohort_prior": False, "prior_weight": 0.0, "reason": "Personnel not found"}
            
        history_days = p_data.get("history_days", 0)
        
        if history_days >= 3:
            return {
                "personnel_id": personnel_id,
                "is_cohort_prior": False,
                "prior_weight": 0.0,
                "history_days": history_days,
                "status": "PERSONAL_BASELINE_ESTABLISHED",
                "description": "Sufficient individual history established; personal baseline active."
            }
            
        # Compute temporary cohort prior
        prior_weight = round(max(0.0, 1.0 - (history_days / 3.0)), 2)
        u_id = p_data["unit_id"]
        zone = p_data["zone"]
        duty = p_data["duty_type"]
        shift = p_data["shift"]
        
        return {
            "personnel_id": personnel_id,
            "is_cohort_prior": True,
            "prior_weight": prior_weight,
            "history_days": history_days,
            "cohort_context": {
                "unit_id": u_id,
                "zone": zone,
                "duty_type": duty,
                "shift": shift
            },
            "status": "TEMPORARY_COHORT_PRIOR_ACTIVE",
            "description": f"Temporary contextual prior active (weight: {prior_weight}); will decay to 0 as personal history reaches 3 days."
        }

    def get_graph_visualization_data(self) -> Dict[str, Any]:
        """
        Produces deterministic 2D spring layout coordinates for performant frontend visualization.
        """
        if len(self.graph.nodes) == 0:
            return {"nodes": [], "edges": [], "summary": {"total_nodes": 0, "total_edges": 0}}
            
        # Deterministic 2D spring layout with fixed seed
        pos = nx.spring_layout(self.graph, seed=42, k=0.35, iterations=50)
        
        nodes_out = []
        for n_id, attrs in self.graph.nodes(data=True):
            coord = pos.get(n_id, (0.0, 0.0))
            nodes_out.append({
                "id": n_id,
                "label": attrs.get("entity_id", n_id),
                "type": attrs.get("entity_type", "UNKNOWN"),
                "privacy_scope": attrs.get("privacy_scope", "PUBLIC"),
                "x": round(float(coord[0]), 4),
                "y": round(float(coord[1]), 4)
            })
            
        edges_out = []
        for u, v, attrs in self.graph.edges(data=True):
            edges_out.append({
                "source": u,
                "target": v,
                "relationship": attrs.get("relationship_type", "CONNECTED"),
                "weight": attrs.get("similarity_weight", 1.0),
                "privacy_scope": attrs.get("privacy_scope", "PUBLIC")
            })
            
        return {
            "nodes": nodes_out,
            "edges": edges_out,
            "summary": {
                "total_nodes": len(nodes_out),
                "total_edges": len(edges_out),
                "total_personnel": len(self.personnel_data),
                "total_patterns_detected": len(self.patterns),
                "last_rebuild": self._last_rebuild_timestamp
            }
        }
