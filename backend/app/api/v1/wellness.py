from fastapi import APIRouter, Depends
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/wellness", tags=["Wellness [Phase 1 Placeholder]"])

@router.get("/")
def get_wellness_records_placeholder(current_user: User = Depends(get_current_user)):
    """
    Placeholder endpoint for Personnel Wellness check-ins.
    """
    return {
        "status": "placeholder",
        "phase": 1,
        "message": "Wellness self-reporting service placeholder",
    }
