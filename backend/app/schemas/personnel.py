from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from shared.schemas.contracts import PersonnelBase
from backend.app.schemas.operational_context import OperationalContextRead

class LeaveReturnRequest(BaseModel):
    leave_type: str = "ANNUAL_LEAVE"
    leave_end_date: datetime
    return_date: datetime

class LeaveEventRead(BaseModel):
    id: str
    personnel_id: str
    leave_type: str
    leave_start_date: Optional[datetime] = None
    leave_end_date: datetime
    return_date: datetime
    transition_days_total: int
    status: str
    recorded_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PersonnelCreate(PersonnelBase):
    user_id: Optional[str] = None
    rank: Optional[str] = None

class PersonnelUpdate(BaseModel):
    unit_id: Optional[str] = None
    role: Optional[str] = None
    posting: Optional[str] = None
    status: Optional[str] = None
    rank: Optional[str] = None

class PersonnelRead(BaseModel):
    id: str
    personnel_id: str
    user_id: Optional[str] = None
    force: str
    unit_id: str
    role: str
    rank: Optional[str] = None
    posting: str
    status: str
    
    # Active operational context
    active_context_id: Optional[str] = None
    current_zone: Optional[str] = None
    current_duty: Optional[str] = None
    current_shift: Optional[str] = None
    current_location: Optional[str] = None
    current_environment: Optional[str] = None
    is_temporary_deployment: bool = False
    
    # Dynamic Countdown info
    remaining_duration_formatted: Optional[str] = None
    remaining_seconds: Optional[int] = None
    assignment_end_time: Optional[datetime] = None
    
    # Post-leave transition
    leave_status: str = "NONE"
    post_leave_day_count: Optional[int] = None # e.g. 1 (Day 1 / 14)
    post_leave_total_days: int = 14
    return_date: Optional[datetime] = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PersonnelDetail(PersonnelRead):
    active_context: Optional[OperationalContextRead] = None
    recent_assignments: List[OperationalContextRead] = []
    leave_events: List[LeaveEventRead] = []
