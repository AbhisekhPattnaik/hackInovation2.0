"""Import all models for SQLAlchemy to recognize them"""
from .user import User
from .doctor import Doctor
from .patient import Patient
from .appointment import Appointment
from .medical_report import MedicalReport
from .queue import QueueEntry, QueueMetrics, QueueOptimization
from .prescription import Prescription

__all__ = [
    "User",
    "Doctor",
    "Patient",
    "Appointment",
    "MedicalReport",
    "QueueEntry",
    "QueueMetrics",
    "QueueOptimization",
    "Prescription"
]
