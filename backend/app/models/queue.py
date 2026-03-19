from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database.config import Base
from datetime import datetime

class QueueEntry(Base):
    """Tracks patient queue position and status"""
    __tablename__ = "queue_entries"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), unique=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    
    # Queue state
    status = Column(String, default="scheduled")  # scheduled, waiting, in_consultation, completed, no_show, cancelled
    queue_position = Column(Integer, nullable=True)  # Position in queue (1, 2, 3...)
    
    # Time tracking
    scheduled_time = Column(DateTime)  # Original scheduled time
    arrival_time = Column(DateTime, nullable=True)  # When patient actually arrived
    consultation_start = Column(DateTime, nullable=True)  # When consultation started
    consultation_end = Column(DateTime, nullable=True)  # When consultation ended
    
    # Predictions (from ML)
    predicted_consultation_duration = Column(Integer, default=15)  # Minutes
    predicted_wait_time = Column(Integer, default=0)  # Minutes
    predicted_no_show_probability = Column(Float, default=0.0)  # ML probability
    
    # Actual observations
    actual_consultation_duration = Column(Integer, nullable=True)  # Minutes (recorded after consultation)
    actual_wait_time = Column(Integer, nullable=True)  # Minutes (actual - real observation)
    
    # Priority and optimization
    priority_score = Column(Float, default=0.5)  # 0-1, higher = more urgent
    optimization_recommended = Column(String, nullable=True)  # "move_earlier", "postpone", "reassign_doctor", "none"
    optimization_reason = Column(Text, nullable=True)  # Explainability: why this was recommended
    optimization_applied = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointment = relationship("Appointment")
    patient = relationship("Patient")
    doctor = relationship("Doctor")

class QueueMetrics(Base):
    """Tracks queue performance metrics for analytics and ML training"""
    __tablename__ = "queue_metrics"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    metric_date = Column(DateTime, default=datetime.utcnow)
    
    # Daily metrics
    total_patients = Column(Integer, default=0)
    avg_wait_time = Column(Float, default=0.0)  # Minutes
    avg_consultation_duration = Column(Float, default=15.0)  # Minutes
    max_queue_length = Column(Integer, default=0)
    no_show_rate = Column(Float, default=0.0)  # Percentage
    late_arrival_rate = Column(Float, default=0.0)  # Percentage
    
    # Prediction accuracy (for retraining)
    prediction_error_duration = Column(Float, default=0.0)  # MAPE or MAE
    prediction_error_wait_time = Column(Float, default=0.0)  # MAPE or MAE
    
    created_at = Column(DateTime, default=datetime.utcnow)
    doctor = relationship("Doctor")

class QueueOptimization(Base):
    """Tracks optimization decisions and their outcomes for Explainable AI"""
    __tablename__ = "queue_optimizations"

    id = Column(Integer, primary_key=True, index=True)
    queue_entry_id = Column(Integer, ForeignKey("queue_entries.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    
    # Decision details
    decision_type = Column(String)  # "slot_shift", "doctor_reassign", "priority_bump", "hold_patient", "expedite"
    original_slot = Column(DateTime)
    recommended_slot = Column(DateTime, nullable=True)
    
    # Explainability
    reasoning = Column(Text)  # Why this decision was made
    factors = Column(Text)  # JSON: factors considered (delays, no-shows, workload, etc)
    confidence_score = Column(Float)  # 0-1, how confident is the model
    
    # Outcome
    was_applied = Column(Boolean, default=False)
    outcome = Column(String, nullable=True)  # "success", "reverted", "pending"
    impact_on_wait_time = Column(Integer, nullable=True)  # Minutes saved/added
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    queue_entry = relationship("QueueEntry")
    doctor = relationship("Doctor")
    patient = relationship("Patient")
