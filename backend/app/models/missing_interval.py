from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, DateTime, Boolean
from backend.app.core.database import Base
from shared.constants.evidence import GapType

class MissingInterval(Base):
    __tablename__ = "missing_intervals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    personnel_id = Column(String(50), nullable=False, index=True)
    signal_name = Column(String(50), nullable=False) # e.g. "hrv", "hr", "sleep", "activity"
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Float, nullable=False)
    gap_type = Column(String(50), default=GapType.SHORT_GAP.value, nullable=False) # SHORT_GAP, LONG_GAP, CONTINUOUS_DROPOUT
    reconstructed = Column(Boolean, default=False, nullable=False)
    reconstruction_method = Column(String(50), nullable=True) # LINEAR_INTERPOLATION, CONSERVATIVE_ESTIMATE, None
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
