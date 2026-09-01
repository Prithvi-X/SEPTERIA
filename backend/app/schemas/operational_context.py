from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field
from shared.schemas.contracts import OperationalContextBase

class OperationalContextCreate(BaseModel):
    name: Optional[str] = None
    personnel_id: Optional[str] = None
    unit_id: Optional[str] = None
    zone: str
    duty_type: str
    shift: str
    location: str
    environment: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    temporary: bool = False
    auto_revert: bool = True
    notes: Optional[str] = None
    source: Optional[str] = "AUTHORITY"

class OperationalContextRead(BaseModel):
    id: str
    name: Optional[str] = None
    personnel_id: Optional[str] = None
    unit_id: Optional[str] = None
    zone: str
    duty_type: str
    shift: str
    location: str
    environment: str
    start_time: datetime
    end_time: Optional[datetime] = None
    temporary: bool
    auto_revert: bool
    status: str
    previous_context_snapshot: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    source: str
    created_at: datetime
    
    # Calculated dynamic fields
    remaining_seconds: Optional[int] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class BulkContextAssignmentRequest(BaseModel):
    assignment_name: str = "Tactical Unit Operational Assignment"
    unit_id: Optional[str] = None
    personnel_ids: Optional[List[str]] = None
    zone: str
    duty_type: str
    shift: str
    location: str
    environment: str
    duration_days: int = 7
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    auto_revert: bool = True
    notes: Optional[str] = None

class BulkAssignmentResponse(BaseModel):
    status: str
    updated_count: int
    message: str
    affected_unit: Optional[str] = None
    assignment_name: str
    zone: str
    auto_revert: bool
    end_time: Optional[datetime] = None
