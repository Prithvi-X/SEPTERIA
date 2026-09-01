from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel

class ZoneDistribution(BaseModel):
    zone_1: int = 0  # High-Intensity / Active Operations
    zone_2: int = 0  # Border / Remote / Extreme Environment
    zone_3: int = 0  # Critical Incident / Post-Incident Recovery
    standard: int = 0

class DashboardMetricsResponse(BaseModel):
    total_personnel: int
    active_units: int
    active_deployments: int
    zone_distribution: ZoneDistribution
    active_temporary_assignments: int
    personnel_in_transition: int
    last_updated: datetime
    data_classification: str = "SYNTHETIC_DEMO_DATA"

class UnitRead(BaseModel):
    id: str
    code: str
    name: str
    force: str
    location: str
    zone: str
    personnel_count: int = 0
