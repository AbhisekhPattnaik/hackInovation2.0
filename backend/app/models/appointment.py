from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Float, Boolean, Text
from sqlalchemy.orm import relationship
from ..database.config import Base
import datetime

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    slot_time = Column(DateTime, default=datetime.datetime.utcnow)
    start_time = Column(DateTime, nullable=True)  # When appointment actually started
    end_time = Column(DateTime, nullable=True)  # When appointment actually ended
    status = Column(String, default="scheduled")  # WAITING, IN_PROGRESS, COMPLETED, RESCHEDULED, NO-SHOW, CANCELLED
    
    # AI scheduling fields
    predicted_wait = Column(Integer, default=0)  # Predicted wait time in minutes
    ai_confidence = Column(Float, default=0.8)  # AI matching confidence (0-1)
    ai_recommended = Column(Boolean, default=False)  # Was this AI recommended?
    
    # Doctor notes and patient review
    doctor_notes = Column(Text, nullable=True)  # Doctor's notes after appointment
    patient_review = Column(Text, nullable=True)  # Patient feedback/review
    symptoms = Column(Text, nullable=True)  # Patient symptoms
    diagnosis = Column(Text, nullable=True)  # Doctor's diagnosis
    
    # Rescheduling tracking
    reschedule_reason = Column(String, nullable=True)  # Why was it rescheduled
    original_slot = Column(DateTime, nullable=True)  # Original scheduled time if rescheduled
    
    # Additional metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    doctor = relationship("Doctor")
    patient = relationship("Patient")