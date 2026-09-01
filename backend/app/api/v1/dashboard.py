from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.api.deps import require_roles
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.dashboard import DashboardMetricsResponse
from backend.app.services.dashboard_service import DashboardService
from shared.constants.roles import UserRole

router = APIRouter(prefix="/dashboard", tags=["Dashboard Metrics"])

@router.get(
    "/metrics",
    response_model=DashboardMetricsResponse,
    summary="Get real-time operational dashboard metrics",
)
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.COMMANDER,
        UserRole.WELFARE_OFFICER,
        UserRole.MEDICAL_OFFICER,
        UserRole.ADMIN,
    )),
):
    """
    Returns aggregate force & unit operational KPIs, zone distribution,
    active temporary assignments, and post-leave transition counts.
    """
    return DashboardService.get_metrics(db=db, current_user=current_user)
