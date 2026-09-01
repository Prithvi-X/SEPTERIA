from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime
from backend.app.core.database import Base

class Unit(Base):
    __tablename__ = "units"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    code = Column(String(50), unique=True, index=True, nullable=False) # e.g. "BSF-BN-47"
    name = Column(String(255), nullable=False)
    force = Column(String(50), nullable=False) # e.g. "BSF", "CRPF"
    location = Column(String(255), nullable=False)
    zone = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
