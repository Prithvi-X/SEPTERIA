from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from shared.constants.roles import UserRole
from backend.app.engine.integration.tri_layer_engine import TriLayerStressEngine, TriLayerConfig

router = APIRouter(prefix="/predictions", tags=["Predictions & Tri-Layer Welfare Gating"])

# Global Engine Singleton
_tri_layer_engine = TriLayerStressEngine()

class WindowInferenceRequest(BaseModel):
    features: Dict[str, Optional[float]] = Field(
        ...,
        description="60-second window wearable features (HR, PRV, EDA, TEMP, ACC)."
    )
    personnel_id: Optional[str] = Field(None, description="Identifier of the personnel member.")
    operational_zone: str = Field(
        default="ZONE_2",
        description="Operational context: ZONE_1 (Active Ops), ZONE_2 (Border/Outpost), or ZONE_3 (Critical Incident)."
    )
    personal_baseline: Optional[Dict[str, float]] = Field(
        None,
        description="Personal baseline reference (hr_median, hr_mad, rmssd_median, rmssd_mad, eda_median)."
    )
    recovery_burden_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Phase 5 composite recovery burden score."
    )
    sleep_deficit_hours: float = Field(
        default=0.0,
        ge=0.0,
        description="Cumulative sleep debt relative to personal baseline."
    )
    trajectory_direction: str = Field(
        default="STABLE",
        description="Autonomic recovery trajectory: IMPROVING, STABLE, or DETERIORATING."
    )
    recent_window_probabilities: List[float] = Field(
        default=[],
        description="List of recent window calibrated probabilities for temporal persistence gating."
    )

@router.get("/model-info")
def get_model_info(current_user: User = Depends(get_current_user)):
    """
    Returns provenance, version, and performance metadata of the Prototype Stress Model.
    """
    cfg = _tri_layer_engine.config
    return {
        "status": "active_prototype",
        "model_version": cfg.model_version,
        "model_designation": cfg.model_designation,
        "is_capf_field_validated": False,
        "tri_layer_architecture": {
            "layer_1": "Prototype ML Physiological Inference (XGBoost)",
            "layer_2": "Personal Baseline & 3-Zone Operational Intelligence",
            "layer_3": "Temporal Persistence Gating & Human-in-the-Loop Welfare Decision"
        },
        "operational_zones": {
            "ZONE_1": "Zone 1: High-Intensity / Active Operations",
            "ZONE_2": "Zone 2: Border / Remote / Extreme Environment",
            "ZONE_3": "Zone 3: Critical Incident / Post-Incident Recovery"
        },
        "regulatory_note": "Research Prototype Decision Support; Not an autonomous clinical diagnostic tool."
    }

@router.post("/inference")
def run_tri_layer_inference(
    payload: WindowInferenceRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Executes real-time inference through the complete Tri-Layer Architecture:
    - Layer 1: XGBoost raw physiological stress likelihood.
    - Layer 2: Exertion disambiguation, personal baseline z-scores, and zone decision gates.
    - Layer 3: Temporal persistence, data quality gating, and advisory recommendations.
    """
    # Authorization check if evaluating a specific personnel member
    if payload.personnel_id and current_user.role == UserRole.PERSONNEL.value:
        if str(current_user.id) != str(payload.personnel_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Personnel may only query their own physiological state."
            )
            
    result = _tri_layer_engine.evaluate_window(
        features=payload.features,
        personnel_id=payload.personnel_id,
        personal_baseline=payload.personal_baseline,
        operational_zone=payload.operational_zone,
        recovery_burden_score=payload.recovery_burden_score,
        sleep_deficit_hours=payload.sleep_deficit_hours,
        trajectory_direction=payload.trajectory_direction,
        recent_window_probabilities=payload.recent_window_probabilities
    )
    return result

@router.get("/personnel/{personnel_id}/current")
def get_current_personnel_welfare(
    personnel_id: str,
    operational_zone: str = "ZONE_2",
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves current contextual welfare assessment for a specific personnel member.
    """
    # RBAC: Soldier can only view self; Medical / Commander can view subordinates
    if current_user.role == UserRole.PERSONNEL.value and str(current_user.id) != str(personnel_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Soldiers are restricted to self-welfare telemetry."
        )
        
    # Mock physiological resting baseline for demo / evaluation
    mock_resting_features = {
        "hr_mean": 72.0, "hr_std": 1.5, "hr_min": 68.0, "hr_max": 76.0, "hr_slope": 0.0,
        "hrv_rmssd": 58.0, "hrv_sdnn": 52.0, "hrv_pnn50": 32.0, "hrv_cv": 7.5,
        "eda_mean": 0.85, "eda_std": 0.05, "eda_min": 0.78, "eda_max": 0.95, "eda_slope": 0.0,
        "eda_tonic_mean": 0.85, "eda_phasic_peaks": 2.0, "eda_phasic_max_amplitude": 0.08, "eda_phasic_auc": 0.25,
        "temp_mean": 33.5, "temp_std": 0.02, "temp_slope": 0.0,
        "acc_magnitude_mean": 63.8, "acc_magnitude_std": 0.35, "acc_motion_energy": 0.12, "acc_peak_acceleration": 65.0
    }
    
    mock_baseline = {
        "hr_median": 70.0, "hr_mad": 2.0,
        "rmssd_median": 60.0, "rmssd_mad": 5.0,
        "eda_median": 0.80
    }
    
    return _tri_layer_engine.evaluate_window(
        features=mock_resting_features,
        personnel_id=personnel_id,
        personal_baseline=mock_baseline,
        operational_zone=operational_zone,
        recovery_burden_score=15.0,
        sleep_deficit_hours=0.5,
        trajectory_direction="STABLE"
    )
