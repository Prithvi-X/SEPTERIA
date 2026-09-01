from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, DateTime
from backend.app.core.database import Base

class EnvironmentalRecord(Base):
    __tablename__ = "environmental_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    location = Column(String(255), nullable=False, index=True)
    unit_id = Column(String(50), nullable=True, index=True)
    ambient_temp = Column(Float, nullable=False) # Ambient temperature in deg C
    altitude = Column(Float, nullable=True) # Altitude in meters
    humidity = Column(Float, nullable=True) # Relative humidity percentage (0-100%)
    environment_category = Column(String(100), nullable=False) # High Heat, Extreme Cold, High Altitude, Standard
    incident_phase = Column(String(100), default="ROUTINE", nullable=False) # ROUTINE, ACTIVE_EXERTION, RECOVERY_WINDOW
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
