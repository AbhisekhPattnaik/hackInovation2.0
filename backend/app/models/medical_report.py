from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary, Text, Enum
from sqlalchemy.orm import relationship
from ..database.config import Base
from datetime import datetime
import enum

class ReportStatus(str, enum.Enum):
    PENDING = "pending"  # Uploaded, awaiting review
    REVIEWED = "reviewed"  # Doctor reviewed
    APPROVED = "approved"  # Doctor approved/confirmed
    FLAGGED = "flagged"  # Issues found
    REJECTED = "rejected"  # Not acceptable
    COMPLETED = "completed"  # Processing complete

class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    uploaded_by = Column(Integer, ForeignKey("users.id"))  # Doctor or Patient who uploaded
    file_name = Column(String, nullable=False)
    file_type = Column(String)  # pdf, jpg, png, etc
    file_data = Column(LargeBinary)  # Binary file data
    diagnosis = Column(String, nullable=True)  # Doctor's notes
    
    # Status tracking
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)  # Pending, Reviewed, Approved, etc
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Doctor who reviewed
    review_notes = Column(Text, nullable=True)  # Doctor's review comments
    reviewed_at = Column(DateTime, nullable=True)  # When it was reviewed
    
    # Report metadata
    report_type = Column(String, nullable=True)  # Lab, X-ray, ECG, etc
    report_description = Column(Text, nullable=True)  # Detailed description
    findings = Column(Text, nullable=True)  # Key findings
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - use foreign_keys argument to disambiguate multiple FK paths
    patient = relationship("Patient")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
