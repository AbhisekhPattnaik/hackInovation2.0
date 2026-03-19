from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Text, Float
from sqlalchemy.orm import relationship
from ..database.config import Base
from datetime import datetime

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), index=True)
    medication = Column(String, index=True)  # Name of medication/diagnosis
    dosage = Column(String, nullable=True)  # e.g., "250mg twice daily"
    duration = Column(String, nullable=True)  # e.g., "7 days", "2 weeks"
    days_supply = Column(Integer, nullable=True)  # Number of days supply
    description = Column(Text, nullable=True)  # Additional notes/instructions
    prescription_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient")
    doctor = relationship("Doctor")
