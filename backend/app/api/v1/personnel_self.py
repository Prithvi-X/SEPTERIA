from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.personnel_self import (
    PersonnelMeResponse,
    AuthoritativeContextRead,
    WellnessCheckInRequest,
    WellnessRecordRead,
    PhysiologicalTrendResponse,
    SupportRequestCreate,
    SupportRequestRead,
    VoiceCheckInRequest,
    VoiceCheckInResponse,
)
from backend.app.schemas.data_pipeline import SignalQualitySummaryResponse
from backend.app.schemas.personal_state import (
    PersonalBaselineResponse,
    PersonalStateResponse,
    TrajectorySummaryResponse,
    ZoneIntelligenceResponse,
)
from backend.app.services.personnel_self_service import PersonnelSelfService
from backend.app.services.personal_state_service import PersonalStateService

router = APIRouter(prefix="/personnel/me", tags=["Personnel Self-Service & Welfare"])

@router.get(
    "",
    response_model=PersonnelMeResponse,
    summary="Get authenticated personnel profile & authoritative operational context",
)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the authenticated jawan's private profile and read-only authoritative operational context.
    """
    return PersonnelSelfService.get_my_profile_and_context(db=db, user=current_user)

@router.get(
    "/context",
    response_model=AuthoritativeContextRead,
    summary="Get authenticated personnel active authoritative context",
)
def get_my_context(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the active authoritative operational context (Zone, Duty, Shift, Countdown).
    """
    profile = PersonnelSelfService.get_my_profile_and_context(db=db, user=current_user)
    return profile.authoritative_context

@router.get(
    "/wellness",
    response_model=List[WellnessRecordRead],
    summary="Get private wellness check-in history",
)
def get_my_wellness_history(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the authenticated jawan's past voluntary check-ins.
    """
    return PersonnelSelfService.get_wellness_history(db=db, user=current_user, limit=limit)

@router.post(
    "/wellness",
    response_model=WellnessRecordRead,
    status_code=status.HTTP_201_CREATED,
    summary="Submit voluntary wellness check-in",
)
def submit_my_wellness_checkin(
    req: WellnessCheckInRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submits and persists a voluntary wellness self-report (stress, fatigue, sleep, mood, workload).
    """
    return PersonnelSelfService.submit_wellness_checkin(db=db, user=current_user, req=req)

@router.get(
    "/trends",
    response_model=PhysiologicalTrendResponse,
    summary="Get personal physiological recovery trends",
)
def get_my_physiological_trends(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns personal trends for HR, HRV, Resting HR, Sleep, and Activity with SQI and evidence status.
    """
    return PersonnelSelfService.get_physiological_trends(db=db, user=current_user, days=days)

@router.get(
    "/quality",
    response_model=SignalQualitySummaryResponse,
    summary="Get multimodal signal quality and data completeness summary",
)
def get_my_signal_quality_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns data completeness score, per-signal SQI, missing intervals, and contextual warnings.
    """
    return PersonnelSelfService.get_signal_quality_summary(db=db, user=current_user)

@router.get(
    "/baseline",
    response_model=PersonalBaselineResponse,
    summary="Get personal baseline metrics with MAD and quality rating",
)
def get_my_personal_baseline(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the authenticated jawan's personal baseline metrics (median, MAD, percentiles, quality).
    """
    personnel = PersonnelSelfService.resolve_personnel_for_user(db, current_user)
    svc = PersonalStateService(db=db)
    return svc.get_or_compute_baseline(personnel_id=personnel.personnel_id)

@router.get(
    "/state",
    response_model=PersonalStateResponse,
    summary="Get current personal state, robust deviations, and recovery debt",
)
def get_my_current_personal_state(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the authenticated jawan's full personal state snapshot including deviations and recovery burden.
    """
    personnel = PersonnelSelfService.resolve_personnel_for_user(db, current_user)
    svc = PersonalStateService(db=db)
    return svc.get_current_personal_state(personnel_id=personnel.personnel_id)

@router.get(
    "/trajectory",
    response_model=TrajectorySummaryResponse,
    summary="Get multi-horizon recovery trajectory summary",
)
def get_my_trajectory_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns multi-horizon recovery trajectory direction, slope, and persistence.
    """
    personnel = PersonnelSelfService.resolve_personnel_for_user(db, current_user)
    svc = PersonalStateService(db=db)
    return svc.get_trajectory_summary(personnel_id=personnel.personnel_id)

@router.get(
    "/context-intelligence",
    response_model=ZoneIntelligenceResponse,
    summary="Get 3-zone contextual evaluation and insights",
)
def get_my_zone_intelligence(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns contextual intelligence conditioned on the active operational zone.
    """
    personnel = PersonnelSelfService.resolve_personnel_for_user(db, current_user)
    svc = PersonalStateService(db=db)
    return svc.get_zone_intelligence(personnel_id=personnel.personnel_id)

@router.post(
    "/support",
    response_model=SupportRequestRead,
    status_code=status.HTTP_201_CREATED,
    summary="Submit confidential welfare support request",
)
def submit_welfare_support_request(
    req: SupportRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submits a confidential welfare support request to the authorized welfare team.
    """
    return PersonnelSelfService.submit_support_request(db=db, user=current_user, req=req)

@router.get(
    "/support",
    response_model=List[SupportRequestRead],
    summary="Get submitted support request status",
)
def get_my_support_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns all support requests submitted by the authenticated jawan and their status.
    """
    return PersonnelSelfService.get_support_requests(db=db, user=current_user)

@router.post(
    "/voice-check-in",
    response_model=VoiceCheckInResponse,
    summary="Submit voluntary voice check-in metadata with consent",
)
def submit_voice_checkin_consent(
    req: VoiceCheckInRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Records voluntary voice check-in acknowledgment with verified user consent.
    """
    return PersonnelSelfService.record_voice_checkin(db=db, user=current_user, req=req)
