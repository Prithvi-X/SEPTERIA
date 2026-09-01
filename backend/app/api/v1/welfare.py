from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.welfare import (
    MultimodalEvaluateRequest,
    MultimodalAssessmentResponse,
    UnitWelfareSummaryResponse,
)
from backend.app.services.welfare_service import WelfareService

router = APIRouter(prefix="/welfare", tags=["Multimodal Welfare Intelligence & Recommendations"])

@router.post(
    "/evaluate",
    response_model=MultimodalAssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute multimodal evidence fusion across all intelligence streams",
)
def evaluate_multimodal_welfare(
    req: MultimodalEvaluateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Executes multimodal evidence fusion combining:
    - Layer 1 XGBoost Physiological Probability
    - Layer 2 Personal Baseline & Zone Gating
    - Layer 5 Autonomic Recovery Trajectory & Sleep Deficit
    - Phase 7 Contextual Personnel Graph Evidence
    - Phase 8 Voluntary Voice Acoustic Deviation
    Returns non-punitive, evidence-based welfare recommendations.
    """
    return WelfareService.evaluate_multimodal(db=db, current_user=current_user, req=req)

@router.get(
    "/personnel/{personnel_id}/current",
    response_model=MultimodalAssessmentResponse,
    summary="Get current multimodal welfare assessment for specific personnel",
)
def get_current_personnel_welfare(
    personnel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns current multimodal welfare assessment for a specific personnel member.
    RBAC: Personnel can only view self; Medical/Welfare officers can view assigned personnel.
    """
    return WelfareService.get_current_welfare(db=db, personnel_id=personnel_id, current_user=current_user)

@router.get(
    "/unit/{unit_id}/summary",
    response_model=UnitWelfareSummaryResponse,
    summary="Get aggregate unit welfare summary for command authority",
)
def get_unit_welfare_summary(
    unit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Command Authority View: Returns aggregate unit welfare distribution, shared distress patterns,
    and operational shift recommendations. Zero individual biometrics or voice metrics are exposed.
    """
    return WelfareService.get_unit_welfare_summary(db=db, unit_id=unit_id, current_user=current_user)
