from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from shared.schemas.contracts import RecommendationBase
from shared.constants.evidence import RecommendationStatus

class RecommendationRead(RecommendationBase):
    id: str
    personnel_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RecommendationStatusUpdate(BaseModel):
    status: RecommendationStatus
