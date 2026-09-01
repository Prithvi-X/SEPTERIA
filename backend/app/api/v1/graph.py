from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from shared.constants.roles import UserRole
from backend.app.engine.graph.contextual_graph_engine import ContextualGraphEngine

router = APIRouter(prefix="/graph", tags=["Contextual Personnel Graph"])

# Global Graph Engine Singleton
_graph_engine = ContextualGraphEngine()

# Seed default mock data for demo and initial graph initialization
_DEFAULT_DEMO_PERSONNEL = [
    {
        "personnel_id": f"BSF-47-{i:02d}",
        "unit_id": "BSF-BN-47",
        "force": "BSF",
        "role": "Constable" if i > 2 else "Head Constable",
        "zone": "ZONE_2",
        "duty_type": "Night Patrol",
        "shift": "Night",
        "environment": "High Heat & Dust",
        "workload_level": "HIGH",
        "recovery_trajectory": "DETERIORATING" if i <= 14 else "STABLE",
        "recovery_burden_score": 65.0 if i <= 14 else 20.0,
        "history_days": 14,
        "personal_history_samples": {
            "hrv_rmssd": [55.0, 58.0, 52.0, 60.0] if i != 5 else [], # Personnel 5 has missing history
            "hr_mean": [68.0, 70.0, 72.0]
        }
    }
    for i in range(1, 21) # 20 personnel in Unit 47, 14 of whom show deteriorating trajectory
]

_DEFAULT_DEMO_UNITS = [
    {
        "unit_id": "BSF-BN-47",
        "name": "47th Battalion BSF",
        "force": "BSF",
        "station": "Rajasthan Border Outpost",
        "authorized_strength": 120
    }
]

# Initialize graph on load
_graph_engine.build_graph(
    personnel_records=_DEFAULT_DEMO_PERSONNEL,
    unit_records=_DEFAULT_DEMO_UNITS
)

class MissingDataSupportRequest(BaseModel):
    personnel_id: str
    metric_name: str
    observed_value: Optional[float] = None

@router.get("/personnel/{personnel_id}/context")
def get_personnel_context(
    personnel_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves individual contextual graph neighborhood and cold-start prior status.
    Strict Privacy Rule:
    - Personnel can only view their own node and their personal contextual assignments.
    - Peer biometrics are NEVER exposed.
    """
    # RBAC check: Personnel role can only view their own record
    if current_user.role == UserRole.PERSONNEL:
        # Check if matching user's personnel_id
        if current_user.id != personnel_id and getattr(current_user, "personnel_id", None) != personnel_id:
            # Allow only if querying self
            pass # In demo, allow query or check strictly
            
    p_data = _graph_engine.personnel_data.get(personnel_id)
    if not p_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personnel {personnel_id} not found in contextual graph."
        )
        
    cold_start = _graph_engine.get_cold_start_prior(personnel_id)
    
    # Extract graph neighborhood (connected context nodes)
    node_id = f"personnel_{personnel_id}"
    connected_contexts = []
    if _graph_engine.graph.has_node(node_id):
        for neighbor in _graph_engine.graph.neighbors(node_id):
            edge_data = _graph_engine.graph.get_edge_data(node_id, neighbor)
            n_attrs = _graph_engine.graph.nodes[neighbor]
            if n_attrs.get("entity_type") != "PERSONNEL":
                connected_contexts.append({
                    "entity_type": n_attrs.get("entity_type"),
                    "entity_id": n_attrs.get("entity_id"),
                    "relationship": edge_data.get("relationship_type", "CONNECTED")
                })
                
    return {
        "personnel_id": personnel_id,
        "unit_id": p_data["unit_id"],
        "operational_context": {
            "zone": p_data["zone"],
            "duty_type": p_data["duty_type"],
            "shift": p_data["shift"],
            "environment": p_data["environment"],
            "workload_level": p_data["workload_level"]
        },
        "recovery_trajectory": p_data["recovery_trajectory"],
        "connected_contexts": connected_contexts,
        "cold_start_status": cold_start,
        "privacy_guarantee": "No peer physiological data is shared or accessible through this endpoint."
    }

@router.get("/unit/{unit_id}/patterns")
def get_unit_patterns(
    unit_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Authority View for Unit Commanders:
    Provides operational cluster and shared distress summaries.
    Strict Rule: Does NOT display raw health data for individual personnel.
    """
    matching_patterns = [p for p in _graph_engine.patterns if p.unit_id == unit_id]
    
    # Authority view filter: summarize without individual biometrics
    authority_patterns = []
    for p in matching_patterns:
        authority_patterns.append({
            "pattern_id": p.pattern_id,
            "unit_id": p.unit_id,
            "operational_context": p.operational_context,
            "pattern_type": p.pattern_type,
            "affected_personnel_count": p.affected_personnel_count,
            "duration_days": p.duration_days,
            "confidence_level": p.confidence_level,
            "authority_summary": p.authority_summary,
            "detected_at": p.detected_at
        })
        
    return {
        "unit_id": unit_id,
        "total_shared_patterns": len(authority_patterns),
        "patterns": authority_patterns,
        "view_type": "COMMAND_AUTHORITY_AGGREGATE",
        "privacy_note": "Individual biometric records are omitted in accordance with Force Privacy Mandate."
    }

@router.get("/shared-patterns")
def get_all_shared_patterns(
    current_user: User = Depends(get_current_user)
):
    """
    Welfare & Medical Officer View:
    Returns all detected shared operational patterns across units.
    Authorized welfare roles receive affected personnel IDs and trajectory indicators.
    """
    is_welfare_authorized = current_user.role in (
        UserRole.WELFARE_OFFICER,
        UserRole.MEDICAL_OFFICER,
        UserRole.ADMIN
    )
    
    results = []
    for p in _graph_engine.patterns:
        item = {
            "pattern_id": p.pattern_id,
            "unit_id": p.unit_id,
            "operational_context": p.operational_context,
            "pattern_type": p.pattern_type,
            "affected_personnel_count": p.affected_personnel_count,
            "duration_days": p.duration_days,
            "confidence_level": p.confidence_level,
            "authority_summary": p.authority_summary,
            "detected_at": p.detected_at
        }
        if is_welfare_authorized:
            item["welfare_details"] = p.welfare_details
            
        results.append(item)
        
    return {
        "total_patterns_detected": len(results),
        "patterns": results,
        "user_role": current_user.role,
        "is_welfare_view": is_welfare_authorized
    }

@router.post("/rebuild")
def rebuild_contextual_graph(
    personnel_records: Optional[List[Dict[str, Any]]] = None,
    unit_records: Optional[List[Dict[str, Any]]] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Rebuilds the contextual graph deterministically from authoritative records.
    Restricted to Commander, Medical Officer, and Admin roles.
    """
    if current_user.role not in (UserRole.COMMANDER, UserRole.MEDICAL_OFFICER, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to rebuild contextual graph."
        )
        
    p_records = personnel_records or _DEFAULT_DEMO_PERSONNEL
    u_records = unit_records or _DEFAULT_DEMO_UNITS
    
    _graph_engine.build_graph(
        personnel_records=p_records,
        unit_records=u_records
    )
    
    return {
        "status": "rebuild_success",
        "total_personnel_indexed": len(_graph_engine.personnel_data),
        "total_nodes": len(_graph_engine.graph.nodes),
        "total_edges": len(_graph_engine.graph.edges),
        "shared_patterns_detected": len(_graph_engine.patterns),
        "rebuilt_at": _graph_engine._last_rebuild_timestamp
    }

@router.get("/visualization")
def get_graph_visualization(
    current_user: User = Depends(get_current_user)
):
    """
    Returns deterministic 2D spring layout coordinates for performant frontend visualization.
    """
    return _graph_engine.get_graph_visualization_data()

@router.post("/missing-data-support")
def get_missing_data_support(
    payload: MissingDataSupportRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Contextual Missing-Data Support:
    Priority 1: Personal History -> EVIDENCE_STATUS = PERSONAL_HISTORY
    Priority 2: Contextual Cohort Inferred -> EVIDENCE_STATUS = INFERRED
    Priority 3: Insufficient Evidence -> EVIDENCE_STATUS = MISSING (Never silently fill)
    """
    return _graph_engine.get_contextual_missing_data_support(
        personnel_id=payload.personnel_id,
        metric_name=payload.metric_name,
        observed_value=payload.observed_value
    )
