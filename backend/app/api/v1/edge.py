from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.edge import (
    EdgeBatchIngestRequest,
    EdgeBatchIngestResponse,
    EdgeDeviceStatusResponse,
    EdgeAuthoritySummaryResponse,
    EdgeDemoStreamRequest,
)
from backend.app.services.edge_service import EdgeService

router = APIRouter(prefix="/edge", tags=["Edge Hardware Ingestion & Offline Sync (Phase 9)"])

@router.post(
    "/telemetry/batch",
    response_model=EdgeBatchIngestResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest batch telemetry from edge wearable/phone with deduplication",
)
def ingest_edge_telemetry_batch(
    req: EdgeBatchIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Ingests batch edge telemetry.
    Enforces idempotency, audits clock drift, and routes valid records into the Phase 4 Quality Pipeline.
    """
    return EdgeService.ingest_edge_batch(db=db, current_user=current_user, req=req)

@router.get(
    "/sync-status",
    response_model=EdgeDeviceStatusResponse,
    summary="Get edge device connectivity and synchronization status",
)
def get_edge_sync_status(
    personnel_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns edge device connection state, pending records count, and last sync timestamp.
    """
    target_id = personnel_id or str(current_user.id)
    return EdgeService.get_device_sync_status(db=db, personnel_id=target_id, current_user=current_user)

@router.post(
    "/demo/simulate-stream",
    summary="Simulate edge wearable stream across 5 demo scenarios with offline toggle",
)
def simulate_edge_demo_stream(
    req: EdgeDemoStreamRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Simulates edge streams:
    - NORMAL_RECOVERY
    - PHYSICAL_EXERTION
    - POOR_SLEEP_RECOVERY_DECLINE
    - SENSOR_DROPOUT
    - CONNECTIVITY_LOSS_SYNC (Simulates offline buffer when simulate_network_disconnect is True)
    """
    return EdgeService.execute_demo_edge_stream(db=db, current_user=current_user, req=req)

@router.get(
    "/authority/overview",
    response_model=EdgeAuthoritySummaryResponse,
    summary="Get aggregate edge device connectivity and sync completeness for commanders",
)
def get_authority_edge_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Command Authority View: Returns aggregate telemetry availability, device connectivity,
    and completeness. Zero private raw biometrics are exposed.
    """
    return EdgeService.get_authority_edge_overview(db=db, current_user=current_user)
