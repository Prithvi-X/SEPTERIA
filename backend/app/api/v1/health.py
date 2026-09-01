from fastapi import APIRouter
from backend.app.schemas.common import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["Health"])
def get_health():
    """
    Health check endpoint returning system status.
    """
    return HealthResponse(
        status="ok",
        service="septeria-api",
        version="0.1.0",
        environment="development",
    )
