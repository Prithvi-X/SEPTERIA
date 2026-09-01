from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

class AuditLogRead(BaseModel):
    id: str
    actor_id: str
    actor_role: str
    action: str
    object_type: str
    object_id: Optional[str] = None
    details: Dict[str, Any]
    timestamp: datetime
    outcome: str

    model_config = ConfigDict(from_attributes=True)
