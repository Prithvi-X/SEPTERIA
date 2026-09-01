from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.data_pipeline import (
    PhysiologicalBatchIngestRequest,
    IngestionResultResponse,
    DemoScenarioRequest,
    DemoScenarioResponse,
)
from backend.app.services.data_pipeline_service import DataPipelineService

router = APIRouter(prefix="/physiology", tags=["Physiology & Ingestion Pipeline"])

@router.post(
    "/ingest",
    response_model=IngestionResultResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest batch physiological telemetry into evidence pipeline",
)
def ingest_physiological_telemetry(
    req: PhysiologicalBatchIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Validates, normalizes, computes SQI, extracts motion context, and persists physiological telemetry.
    """
    raw_dicts = [item.model_dump() for item in req.records]
    return DataPipelineService.ingest_records(
        db=db,
        personnel_id=req.personnel_id,
        raw_items=raw_dicts,
        adapter_source=req.adapter_source or "api_adapter",
        actor_id=current_user.id,
        actor_role=current_user.role,
    )

@router.post(
    "/demo/scenario",
    response_model=DemoScenarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute reproducible synthetic demonstration scenario",
)
def run_demo_scenario(
    req: DemoScenarioRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generates and processes one of 7 synthetic test scenarios (A: Normal, B: Exertion, C: Heat, D: Recovery Decline, E: 20-min Missing HRV, F: Post-Leave, G: Contradictory).
    """
    return DataPipelineService.execute_demo_scenario(
        db=db,
        scenario_code=req.scenario_code,
        personnel_id=req.personnel_id or "P-1047",
        days=req.days or 7,
    )

@router.get(
    "/scenarios",
    summary="List available synthetic demonstration scenarios",
)
def list_available_scenarios(
    current_user: User = Depends(get_current_user),
):
    """
    Returns the catalog of 7 reproducible synthetic demonstration scenarios.
    """
    return {
        "scenarios": [
            {"code": "A", "name": "Normal Recovery Baseline", "description": "Stable physiological equilibrium (HR ~70, HRV ~56 ms, Sleep ~7.2h)."},
            {"code": "B", "name": "Physical Exertion Protocol", "description": "High HR + High Activity contextualized as physical exertion."},
            {"code": "C", "name": "High Heat & Physical Exertion", "description": "Ambient 44°C desert thermal stress combined with patrol movement."},
            {"code": "D", "name": "Recovery Decline (Sleep & Workload Strain)", "description": "Cumulative sleep restriction, increasing resting HR, and declining HRV trajectory."},
            {"code": "E", "name": "Sensor Dropout (20-Minute Missing HRV Segment)", "description": "Injects exact 20-minute gap, detects missing interval, and tags conservative reconstructions as INFERRED."},
            {"code": "F", "name": "Post-Leave Transition Deterioration", "description": "Day 3/14 reintegration friction with shift adaptation strain."},
            {"code": "G", "name": "Contradictory Signals Assessment", "description": "Normal sleep self-report with elevated resting HR flagged for contextual review."},
        ]
    }
