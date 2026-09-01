from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.api.deps import require_roles
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.audit_log import AuditLog
from backend.app.schemas.audit import AuditLogRead
from shared.constants.roles import UserRole

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])

@router.get(
    "/",
    response_model=List[AuditLogRead],
    summary="List system audit logs for administrative governance",
)
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.ADMIN,
    )),
):
    """
    Least-Privilege: Only System Admin has access to full system audit logs.
    """
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    return logs
