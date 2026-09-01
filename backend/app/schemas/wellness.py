from datetime import datetime
from typing import Optional
from pydantic import ConfigDict
from shared.schemas.contracts import WellnessRecordBase

class WellnessRecordCreate(WellnessRecordBase):
    personnel_id: Optional[str] = None

class WellnessRecordRead(WellnessRecordBase):
    id: str
    personnel_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
