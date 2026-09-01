from datetime import datetime
import uuid
from sqlalchemy import Column, String, Text, DateTime
from backend.app.core.database import Base
from shared.constants.evidence import RecommendationPriority, RecommendationStatus

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    personnel_id = Column(String(50), nullable=False, index=True)
    type = Column(String(100), nullable=False) # e.g. REST_ADVISORY, WELFARE_CHECK, DUTY_ROTATION
    priority = Column(String(50), default=RecommendationPriority.ROUTINE.value, nullable=False)
    explanation = Column(Text, nullable=False)
    status = Column(String(50), default=RecommendationStatus.PENDING.value, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
