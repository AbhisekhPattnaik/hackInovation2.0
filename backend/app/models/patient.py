from sqlalchemy import Column, Integer, Float, ForeignKey, String, DateTime, Text
from sqlalchemy.orm import relationship
from ..database.config import Base
from datetime import datetime
import uuid

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ps_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4())[:8].upper())  # Patient System ID
    severity_score = Column(Float, default=0.0)
    predicted_duration = Column(Integer, default=15)  # ML-predicted consultation time in minutes
    avg_historical_duration = Column(Float, default=15)  # Historical average for ML training
    no_show_count = Column(Integer, default=0)  # No-show history for ML
    late_arrival_count = Column(Integer, default=0)  # Late arrivals for ML
    priority_score = Column(Float, default=0.5)  # ML-calculated priority (0-1)
    
    # Extended fields for patient dashboard
    symptoms = Column(Text, nullable=True)  # Patient reported symptoms
    age = Column(Integer, nullable=True)
    ai_priority = Column(String, default="NORMAL")  # LOW, NORMAL, HIGH, URGENT
    recommended_doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User")