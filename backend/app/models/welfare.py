import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON, Text, ForeignKey
from backend.app.core.database import Base

class MultimodalAssessmentRecord(Base):
    __tablename__ = "multimodal_assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    personnel_id = Column(String(50), nullable=False, index=True)
    advisory_welfare_state = Column(String(50), nullable=False)
    composite_welfare_score = Column(Float, nullable=False)
    multimodal_confidence = Column(Float, nullable=False)
    evidence_agreement_score = Column(Float, nullable=False)
    is_evidence_conflict = Column(Boolean, default=False, nullable=False)
    conflict_details = Column(Text, nullable=True)
    contributing_streams_json = Column(JSON, nullable=True)
    voice_included = Column(Boolean, default=False, nullable=False)
    graph_included = Column(Boolean, default=False, nullable=False)
    recommended_action = Column(Text, nullable=False)
    human_review_required = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
