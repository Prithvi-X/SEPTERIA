from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.api.deps import get_current_user, require_roles
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.services.system_service import SystemService
from shared.constants.roles import UserRole

router = APIRouter(prefix="/system", tags=["System Administration & Demo Management (Phase 10)"])

@router.post(
    "/reset-demo",
    status_code=status.HTTP_200_OK,
    summary="Reset synthetic demo state for repeatable demonstrations",
)
def reset_demo_state(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.COMMANDER)),
):
    """
    Cleans synthetic telemetry, voice check-ins, welfare assessments, and edge sync records,
    restoring a clean baseline for reproducible demonstration. Restricted to Admin/Commander.
    """
    return SystemService.reset_demo_state(
        db=db,
        actor_id=str(current_user.id),
        actor_role=current_user.role
    )

@router.get(
    "/health-audit",
    summary="Multi-subsystem health audit and claim boundaries verification",
)
def get_system_health(
    db: Session = Depends(get_db),
):
    """
    Audits all 9 core subsystems (ML, Tri-Layer, Graph, Voice, Edge, Sync, Database)
    and verifies ethical claim boundaries.
    """
    return SystemService.get_system_health(db=db)
