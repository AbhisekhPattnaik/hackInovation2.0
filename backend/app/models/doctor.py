from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..database.config import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    specialization = Column(String)
    avg_consult_time = Column(Integer, default=15)
    utilization = Column(Float, default=0.0)
    
    # Extended fields for admin monitoring
    years_of_experience = Column(Integer, default=0)
    medical_license_number = Column(String, nullable=True)
    hospital_affiliation = Column(String, nullable=True)
    rating = Column(Float, default=0.0)
    verification_status = Column(String, default="PENDING")  # PENDING, VERIFIED, REJECTED
    
    user = relationship("User")