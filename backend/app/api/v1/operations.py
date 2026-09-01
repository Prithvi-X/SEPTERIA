from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.api.deps import get_current_user, require_roles
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.operational_context import (
    OperationalContextCreate,
    OperationalContextRead,
    BulkContextAssignmentRequest,
    BulkAssignmentResponse,
)
from backend.app.services.operations_service import OperationsService
from backend.app.services.personal_state_service import PersonalStateService
from shared.constants.roles import UserRole

router = APIRouter(prefix="/operations", tags=["Operational Context & Deployments"])

@router.get(
    "/",
    summary="List active & historical operational contexts",
)
def list_operations(
    unit_id: Optional[str] = Query(None, description="Filter by Unit ID"),
    personnel_id: Optional[str] = Query(None, description="Filter by Personnel ID"),
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE, REVERTED, EXPIRED)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.COMMANDER,
        UserRole.WELFARE_OFFICER,
        UserRole.MEDICAL_OFFICER,
        UserRole.ADMIN,
    )),
):
    """
    Least-Privilege: Authority roles can view active operational assignments.
    """
    return OperationsService.get_operations(
        db=db,
        unit_id=unit_id,
        personnel_id=personnel_id,
        status=status,
        skip=skip,
        limit=limit,
    )

@router.get(
    "/zone-intelligence-summary",
    summary="Get aggregated operational readiness and zone distribution summary",
)
def get_zone_intelligence_summary(
    unit_id: Optional[str] = Query(None, description="Optional unit ID filter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.COMMANDER,
        UserRole.WELFARE_OFFICER,
        UserRole.MEDICAL_OFFICER,
        UserRole.ADMIN,
    )),
):
    """
    Least-Privilege: Provides aggregated operational zone distribution and stream synchronization summary.
    Zero raw personal wellness or clinical telemetry is exposed to commander roles.
    """
    svc = PersonalStateService(db=db)
    return svc.get_aggregate_zone_summary(unit_id=unit_id)

@router.post(
    "/",
    response_model=OperationalContextRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create operational assignment",
)
def create_operation(
    data: OperationalContextCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.COMMANDER,
        UserRole.ADMIN,
    )),
):
    """
    Least-Privilege: Only Unit Commanders (and Admin override) can create tactical operational assignments.
    Welfare and Medical officers are forbidden from modifying tactical assignments.
    """
    if data.end_time and data.start_time and data.end_time <= data.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignment end time must be strictly after start time",
        )
    return OperationsService.create_assignment(db=db, data=data, actor=current_user)

@router.post(
    "/bulk-assign",
    response_model=BulkAssignmentResponse,
    summary="Bulk assign operational context to unit or selected personnel",
)
def bulk_assign_operation(
    req: BulkContextAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.COMMANDER,
        UserRole.ADMIN,
    )),
):
    """
    Least-Privilege: Only Unit Commanders and Admin can execute bulk operational duty/zone/shift assignments.
    """
    if req.end_time and req.start_time and req.end_time <= req.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignment end time must be strictly after start time",
        )
    return OperationsService.bulk_assign_context(db=db, req=req, actor=current_user)

@router.post(
    "/evaluate-reversions",
    summary="Trigger automatic reversion check for expired temporary assignments",
)
def evaluate_reversions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.ADMIN,
        UserRole.COMMANDER,
    )),
):
    """
    Evaluates all active assignments, reverts expired ones, and records audit logs.
    """
    reverted_count = OperationsService.evaluate_and_revert_expired(db, force_actor_email=current_user.email)
    return {
        "status": "success",
        "reverted_count": reverted_count,
        "message": f"Evaluated temporary assignments: {reverted_count} expired assignments automatically reverted.",
    }
