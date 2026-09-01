from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.api.deps import get_current_user, require_roles
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.personnel import PersonnelRead, PersonnelDetail, LeaveReturnRequest
from backend.app.schemas.personal_state import PersonalBaselineResponse, PersonalStateResponse
from backend.app.services.personnel_service import PersonnelService
from backend.app.services.personal_state_service import PersonalStateService
from shared.constants.roles import UserRole

router = APIRouter(prefix="/personnel", tags=["Personnel Directory"])

@router.get(
    "/",
    response_model=List[PersonnelRead],
    summary="List and filter personnel directory",
)
def list_personnel(
    search: Optional[str] = Query(None, description="Search query by Personnel ID, Rank, Force"),
    force: Optional[str] = Query(None, description="Filter by Force (BSF, CRPF, ITBP, etc.)"),
    unit_id: Optional[str] = Query(None, description="Filter by Unit ID"),
    zone: Optional[str] = Query(None, description="Filter by Operational Zone"),
    duty: Optional[str] = Query(None, description="Filter by Duty Type"),
    shift: Optional[str] = Query(None, description="Filter by Shift"),
    status: Optional[str] = Query(None, description="Filter by Status (ACTIVE, DEPLOYED, TRANSITION)"),
    leave_status: Optional[str] = Query(None, description="Filter by Leave Status (POST_LEAVE_TRANSITION, ON_LEAVE)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.COMMANDER,
        UserRole.WELFARE_OFFICER,
        UserRole.MEDICAL_OFFICER,
        UserRole.ADMIN,
    )),
):
    """
    Least-Privilege: Authority roles (Commander, Welfare Officer, Medical Officer, Admin)
    can view personnel directory. Personnel role has NO access to authority portal.
    """
    personnel_list, _ = PersonnelService.list_personnel(
        db=db,
        search=search,
        force=force,
        unit_id=unit_id,
        zone=zone,
        duty=duty,
        shift=shift,
        status=status,
        leave_status=leave_status,
        skip=skip,
        limit=limit,
    )
    return personnel_list

@router.get(
    "/{personnel_id}",
    response_model=PersonnelDetail,
    summary="Get personnel administrative profile",
)
def get_personnel_profile(
    personnel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.COMMANDER,
        UserRole.WELFARE_OFFICER,
        UserRole.MEDICAL_OFFICER,
        UserRole.ADMIN,
    )),
):
    """
    Get detailed administrative profile with dynamic countdown and post-leave transition tracker.
    """
    profile = PersonnelService.get_personnel_profile(db=db, personnel_id=personnel_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personnel with ID '{personnel_id}' not found",
        )
    return profile

@router.get(
    "/{personnel_id}/baseline",
    response_model=PersonalBaselineResponse,
    summary="Get personnel personal baseline metrics (Welfare/Medical/Admin only)",
)
def get_personnel_baseline(
    personnel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.WELFARE_OFFICER,
        UserRole.MEDICAL_OFFICER,
        UserRole.ADMIN,
    )),
):
    """
    Least-Privilege: Authorized Welfare and Medical officers can inspect personal baselines.
    """
    svc = PersonalStateService(db=db)
    return svc.get_or_compute_baseline(personnel_id=personnel_id)

@router.get(
    "/{personnel_id}/state",
    response_model=PersonalStateResponse,
    summary="Get personnel current state, deviations, and recovery debt (Welfare/Medical/Admin only)",
)
def get_personnel_state(
    personnel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.WELFARE_OFFICER,
        UserRole.MEDICAL_OFFICER,
        UserRole.ADMIN,
    )),
):
    """
    Least-Privilege: Authorized Welfare and Medical officers can inspect personal state snapshots.
    """
    svc = PersonalStateService(db=db)
    return svc.get_current_personal_state(personnel_id=personnel_id)

@router.post(
    "/{personnel_id}/leave-return",
    summary="Record return from leave and trigger post-leave transition window",
)
def record_leave_return(
    personnel_id: str,
    req: LeaveReturnRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.WELFARE_OFFICER,
        UserRole.COMMANDER,
        UserRole.ADMIN,
    )),
):
    """
    Least-Privilege: Welfare Officer (Primary) and Commander/Admin can record return from leave.
    Activates the 14-day transition window (Day X / 14).
    """
    try:
        result = PersonnelService.record_leave_return(
            db=db,
            personnel_id=personnel_id,
            req=req,
            actor=current_user,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
