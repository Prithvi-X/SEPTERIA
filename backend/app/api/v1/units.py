from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.api.deps import require_roles
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.unit import Unit
from backend.app.models.personnel import Personnel
from backend.app.schemas.dashboard import UnitRead
from shared.constants.roles import UserRole

router = APIRouter(prefix="/units", tags=["Force Units"])

@router.get(
    "/",
    response_model=List[UnitRead],
    summary="List synthetic force battalions / units",
)
def list_units(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.COMMANDER,
        UserRole.WELFARE_OFFICER,
        UserRole.MEDICAL_OFFICER,
        UserRole.ADMIN,
    )),
):
    units = db.query(Unit).order_by(Unit.code.asc()).all()
    result = []
    for u in units:
        count = db.query(Personnel).filter(Personnel.unit_id == u.code).count()
        result.append(UnitRead(
            id=u.id,
            code=u.code,
            name=u.name,
            force=u.force,
            location=u.location,
            zone=u.zone,
            personnel_count=count,
        ))
    return result
